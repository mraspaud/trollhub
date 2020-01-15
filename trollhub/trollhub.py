
import os
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file

app = Flask(__name__)

BASECOORDS = [-13.9626, 33.7741]


@app.route('/')
def index():
    """Index."""
    return render_template('index.html')


@app.route('/getFile/<int:file_id>') # this is a job for GET, not POST
def get_file(file_id):
    """Get the file."""
    print('File requested: %d'%file_id)
    return jsonify(file_id)


@app.route('/getFile2', methods=['POST']) # this is a job for GET, not POST
def get_file2():
    """Get the file."""
    data = request.form['javascript_data']

    print('thedata')
    print(data)
    return data


@app.route('/search', methods=['POST'])
def search():
    """Search matching passes."""
    from shapely.geometry import shape, mapping
    print(request.json)
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

    from shapely.ops import cascaded_union
    req_poly = cascaded_union(polygons)

    features = []
    search_funs = {'Local archive': search_local_safe,
                   'Mongo': search_mongo}
    search_fun = search_funs.get(js['sourceID'], None)

    if search_fun is None:
        return jsonify({})

    if js['sourceID'] == "Local archive":
        for footprint, properties in search_fun():
            if (properties['start_time'] > end_time) or (properties['end_time'] < start_time):
                continue
            if req_poly.intersects(footprint):
                filename = properties['uid']
                features.append(dict(type='Feature', properties={'id': os.path.basename(filename), 'quicklook': os.path.join(filename, 'preview', 'quick-look.png'), 'pass_direction': properties['pass_direction']}, geometry=mapping(footprint)))

        return jsonify({'features': features})

    elif js['sourceID'] == 'Mongo':
        docs = search_mongo(start_time, end_time)
        for doc in docs:
            footprint = doc['boundary']
            id = doc['uid']
            if 'dataset' in doc:
                doc['uri'] = doc['dataset'][0]['uri']
            props = {'id': id, 'pass_direction': doc['pass_direction']}
            for optional in ['uri', 'quicklook']:
                try:
                    props[optional] = doc[optional]
                except KeyError:
                    pass
            features.append(dict(type='Feature', properties=props, geometry=footprint))

        return jsonify({'features': features})


def search_mongo(start_time, end_time):
    """Search from a mongo db."""
    from pymongo import MongoClient
    client = MongoClient(app.config['mongo_uri'])
    docs = client.sat_db.files
    return docs.find({'start_time': {'$lte': end_time},
                      'end_time': {'$gte': start_time},
                      'sensor': 'sar-c'})


def search_local_safe():
    """Search locally."""
    import xml.etree.ElementTree as ET
    import glob
    from shapely import geometry
    #safe_files = glob.glob('/home/a001673/data/satellite/Sentinel-1/*/*.safe')
    safe_files = glob.glob('/data/24/saf/polar_in/sentinel1/sar-c/lvl1/*/*.safe')
    for safe_file in safe_files:
        my_namespaces = dict([
              node for _, node in ET.iterparse(
                  safe_file, events=['start-ns']
              )
          ])

        tree = ET.parse(safe_file)
        root = tree.getroot()
        #root.find('*//safe:footPrint', my_namespaces)
        coords = root.find('*//safe:footPrint/gml:coordinates', my_namespaces).text.split()
        footprint = [[float(x) for x in elt.split(',')] for elt in coords]
        poly = geometry.Polygon([[p[1], p[0]] for p in footprint])
        pass_direction = root.find('*//s1:orbitProperties/s1:pass', my_namespaces).text.strip()
        start_time = root.find('*//safe:acquisitionPeriod/safe:startTime', my_namespaces).text.strip()
        start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%f')
        end_time = root.find('*//safe:acquisitionPeriod/safe:stopTime', my_namespaces).text.strip()
        end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%f')
        properties = dict(uid=os.path.dirname(safe_file),
                          pass_direction=pass_direction,
                          start_time=start_time,
                          end_time=end_time)
        yield poly, properties


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Catch all function."""
    print('You want path: %s' % path)
    return send_file(os.path.join('/', path))


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-m', '--mongo-uri')
    args = parser.parse_args()
    app.config['mongo_uri'] = args.mongo_uri
    app.run(host='0.0.0.0', debug=True)
