
import os
from datetime import datetime
import trollsift

from flask import Flask, jsonify, render_template, request, send_file, abort
import logging

logger = logging.getLogger('trollhub')

app = Flask(__name__)

allowed_urls = set()


@app.route('/')
def index():
    """Index."""
    source_list = app.config["SOURCES"].keys()
    base_coords = app.config["BASECOORDS"]
    return render_template('index.html', source_list=source_list,
                           center_lon=base_coords["lon"],
                           center_lat=base_coords["lat"])


@app.route('/search', methods=['POST'])
def search():
    """Search matching passes."""
    from shapely.geometry import shape, mapping
    logger.warning(str(request.json))
    js = request.json

    polygons = []
    for feature in js['features']:
        try:
            polygons.append(shape(feature['geometry']))
        except KeyError:
            pass

    start_time = js['start_time']
    start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    end_time = js['end_time']
    end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')

    from shapely.ops import unary_union
    req_poly = unary_union(polygons)

    features = []
    try:
        db_access = app.config["SOURCES"][js['sourceID']]
    except KeyError:
        return jsonify({})

    if db_access.endswith(".tif"):
        search_fun = search_local_tiffs
    elif db_access.endswith(".safe"):
        search_fun = search_local_safe
    elif ":" in db_access:
        search_fun = search_mongo
    else:
        logger.error("Unrecognize db type: %s", db_access)
        return jsonify({})

    global allowed_urls
    allowed_urls = set()

    for footprint, properties in search_fun(db_access, start_time, end_time):
        if req_poly.is_empty or req_poly.intersects(footprint):
            feature = dict(type='Feature', properties=properties,
                           geometry=mapping(footprint))
            if "quicklook" in properties:
                allowed_urls.add(properties['quicklook'])
            features.append(feature)
    return jsonify({'features': features})


def search_mongo(db_access, start_time, end_time):
    """Search from a mongo db."""
    from pymongo import MongoClient
    from shapely import geometry
    client = MongoClient(db_access)
    docs = client.sat_db.files
    docs = docs.find({'start_time': {'$lte': end_time},
                      'end_time': {'$gte': start_time},
                      'sensor': 'sar-c',
                      'format': 'SAFE',})
    for doc in docs:
        poly = geometry.Polygon(doc["boundary"]["coordinates"][0])

        properties = {"id": doc["uid"],
                      "pass_direction": doc["pass_direction"],
                      "quicklook": doc["quicklook"]}
        yield poly, properties


def search_local_safe(pattern, req_start_time, req_end_time):
    """Search locally."""
    import xml.etree.ElementTree as ET
    import glob
    from shapely import geometry
    parser = trollsift.Parser(pattern)
    safe_files = glob.glob(parser.globify())

    for safe_file in safe_files:
        my_namespaces = dict([
              node for _, node in ET.iterparse(
                  safe_file, events=['start-ns']
              )
          ])

        tree = ET.parse(safe_file)
        root = tree.getroot()

        start_time = root.find('*//safe:acquisitionPeriod/safe:startTime', my_namespaces).text.strip()
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f')
        end_time = root.find('*//safe:acquisitionPeriod/safe:stopTime', my_namespaces).text.strip()
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')

        if (start_time > req_end_time) or (end_time < req_start_time):
            continue

        pass_direction = root.find('*//s1:orbitProperties/s1:pass', my_namespaces).text.strip()
        quicklook_path = os.path.join(os.path.dirname(safe_file), 'preview', 'quick-look.png')
        coords = root.find('*//safe:footPrint/gml:coordinates', my_namespaces).text.split()
        footprint = [[float(x) for x in elt.split(',')] for elt in coords]
        poly = geometry.Polygon([[p[1], p[0]] for p in footprint])


        properties = dict(id=os.path.basename(os.path.dirname(safe_file)),
                          quicklook=quicklook_path,
                          pass_direction=pass_direction.lower())

        yield poly, properties


def search_local_tiffs(pattern, req_start_time, req_end_time):
    """Search locally."""
    import glob
    from shapely import geometry
    from osgeo import gdal
    parser = trollsift.Parser(pattern)
    files = glob.glob(parser.globify())

    for pathname in files:
        mda = parser.parse(pathname)

        pass_direction = 'ascending'

        end_time = start_time = mda["start_time"]

        if (start_time > req_end_time) or (end_time < req_start_time):
            continue

        info = gdal.Info(pathname, format='json')
        poly = geometry.shape(info['wgs84Extent'])

        properties = dict(id=os.path.basename(pathname),
                          pass_direction=pass_direction)
        yield poly, properties


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Catch all function."""
    path = os.path.join('/', path)
    if path not in allowed_urls:
        abort(404)
    return send_file(path)


def create_app(config):
    if isinstance(config, dict):
        app.config.update(config)
    else:
        import yaml
        with open(config) as fd:
            mapping = yaml.safe_load(fd.read())
            app.config.from_mapping(mapping)
    return app


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument('-c', '--config')
    args = parser.parse_args()
    app = create_app(args.config)
    app.run(host='0.0.0.0')
