import sys
import random
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
from flask import send_file


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'

db = SQLAlchemy(app)

BASECOORDS = [-13.9626, 33.7741]


@app.route('/')
def index():
    return render_template('index.html')

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

@app.route('/search', methods=['POST'])
def search():
    from shapely.geometry import shape
    print(request.json)
    js = {'features': [request.json]}
    with open('./testpolygon.geojson') as json_data:
        item = json.load(json_data)
    test_poly = shape(item['features'][0]['geometry'])
    for feature in js['features']:
        polygon = shape(feature['poly']['geometry'])
        if polygon.intersects(test_poly):
            print('Found containing polygon:', feature)
            return jsonify(item)
        else:
            return jsonify({})

if __name__ == '__main__':
    app.run(debug=True)
