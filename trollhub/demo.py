import sys
import random
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json
from flask import send_file
import os
# from flask_cas import CAS, login_required

app = Flask(__name__)
# cas = CAS(app, '/cas')
# app.config['CAS_SERVER'] = 'https://websso-tst.smhi.se'
# app.config['CAS_AFTER_LOGIN'] = 'root'
# app.secret_key = 'super secret key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#
# db = SQLAlchemy(app)

BASECOORDS = [-13.9626, 33.7741]


@app.route('/')
#@login_required
def index():
    return render_template('index.html')
                           #, username=cas.username,
                                #         display_name=cas.attributes['cas:displayName'])

@app.route('/getFile/<int:file_id>') # this is a job for GET, not POST
def get_file(file_id):
    print('File requested: %d'%file_id)
    return jsonify(file_id)

@app.route('/getFile2', methods=['POST']) # this is a job for GET, not POST
def get_file2():
    data = request.form['javascript_data']

    print('thedata')
    print(data)
    #print('File requested: %d'%file_id)
    return data

@app.route('/searchold', methods=['POST'])
def searchold():
    from shapely.geometry import shape
    print(request.json)
    js = {'features': [request.json]}
    with open('./testpolygon.geojson') as json_data:
        item = json.load(json_data)
    test_poly = shape(item['features'][0]['geometry'])

    for feature in js['features']:
        try:
            polygon = shape(feature['poly']['geometry'])
            if polygon.intersects(test_poly):
                print('Found containing polygon:', feature)
                return jsonify(item)
            else:
                return jsonify({})
        except KeyError:
            pass

@app.route('/search', methods=['POST'])
def search():
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
    search_funs = {'Local archive': search_local_safe}
    search_fun = search_funs.get(js['sourceID'], None)

    if search_fun is None:
        return jsonify({})

    for footprint, properties in search_fun():
        if (properties['start_time'] > end_time) or (properties['end_time'] < start_time):
            continue
        if req_poly.intersects(footprint):
            filename = properties['uid']
            features.append(dict(type='Feature', properties={'id': os.path.basename(filename), 'quicklook': os.path.join(filename, 'preview', 'quick-look.png'), 'pass_direction': properties['pass_direction']}, geometry=mapping(footprint)))
    return jsonify({'features': features})



def search_local_safe():
    import xml.etree.ElementTree as ET
    import glob
    from shapely import geometry
    #safe_files = glob.glob('/home/a001673/data/satellite/Sentinel-1/*/*.safe')
    safe_files = glob.glob('/data/prod/satellit/sentinel1/sar-c/lvl1/*/*.safe')
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
    #return 'You want path: %s' % path
    print('You want path: %s' % path)
    return send_file(os.path.join('/', path))

if __name__ == '__main__':
    print(app.instance_path)
    app.run(debug=True)
