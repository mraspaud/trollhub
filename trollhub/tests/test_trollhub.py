import pytest
from trollhub import create_app
import os
import json
import shutil
from unittest.mock import patch, MagicMock
import datetime

@pytest.fixture
def client():
    #app = create_app({'TESTING': True})
    pathname = os.path.join(os.path.dirname(__file__), "testconfig.yaml")
    app = create_app(pathname)
    with app.test_client() as client:
        yield client

def test_app_created(client):
    rv = client.get('/etc/passwd')
    assert rv.status_code == 404

def test_index(client):
    response = client.get("/", content_type="html/text")

    assert response.status_code == 200
    assert response.data.startswith(b"<html>")

def test_config_is_read(client):
    assert "SOURCES" in client.application.config

class TestSearch:

    def setup(self):
        self.tiffdir = '/tmp/tiffdir'
        self.safedir = '/tmp/safedir'
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'tiffdir'), self.tiffdir)
        shutil.copytree(os.path.join(os.path.dirname(__file__), 'safedir'), self.safedir)

    def test_search_tiffs(self, client):
        req_dict = {'type': 'FeatureCollection', 'features': [], 'sourceID': 'tiffs',
                    'start_time': '2022-02-02T11:52:00.000Z', 'end_time': '2022-02-04T11:52:00.000Z'}
        rv = client.post('/search', data=json.dumps(req_dict), content_type='application/json')
        assert rv.status_code == 200
        res = json.loads(rv.data)
        assert res == {'features': [{'geometry': {'coordinates': [[[14.336046, 53.9570936], [14.336046, 53.5847923],
                                                                   [14.7906833, 53.5847923], [14.7906833, 53.9570936],
                                                                   [14.336046, 53.9570936]]], 'type': 'Polygon'},
                                     'properties': {'id': '20220203050856_S1A_IW_VV_30m.tif',
                                                    'pass_direction': 'ascending'},
                                     'type': 'Feature'}]}

    def test_search_safes(self, client):
        req_dict = {'type': 'FeatureCollection', 'features': [], 'sourceID': 'safes',
                    'start_time': '2022-02-02T11:52:00.000Z', 'end_time': '2022-02-04T11:52:00.000Z'}
        rv = client.post('/search', data=json.dumps(req_dict), content_type='application/json')
        assert rv.status_code == 200
        res = json.loads(rv.data)
        assert res == {'features': [{'geometry': {'coordinates': [[[18.168846, 52.048065], [14.335609, 52.462574],
                                                                   [14.713546, 53.95718], [18.680494, 53.539776],
                                                                   [18.168846, 52.048065]]],
                                                  'type': 'Polygon'},
                                     'properties': {'id': 'S1A_IW_GRDH_1SDV_20220203T050856_20220203T050921_041744_04F7A3_E41E.SAFE',  # noqa
                                                    'pass_direction': 'DESCENDING',
                                                    'quicklook': '/tmp/safedir/S1A_IW_GRDH_1SDV_20220203T050856_20220203T050921_041744_04F7A3_E41E.SAFE/preview/quick-look.png'},  # noqa
                                     'type': 'Feature'}]}

    @patch('pymongo.MongoClient')
    def test_search_mongo(self, mongoclient, client):

        ObjectId = MagicMock
        find_result = [{'_id': ObjectId('61fabb17a717ba56392b3b85'), 'platform_name': 'S1A', 'scan_mode': 'IW',
                        'type': 'GRDH', 'data_source': '1SDV',
                        'start_time': datetime.datetime(2022, 2, 2, 15, 40, 11, 657000),
                        'end_time': datetime.datetime(2022, 2, 2, 15, 40, 40, 688000),
                        'orbit_number': 41736, 'random_string1': '04F765', 'random_string2': 'E57A',
                        'dataset':
                            [{
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE-report-20220202T164128.pdf',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE-report-20220202T164128.pdf',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE'}, {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/calibration-s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/calibration-s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/calibration-s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/calibration-s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/noise-s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/noise-s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/noise-s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration/noise-s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/calibration'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/rfi/rfi-s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/rfi/rfi-s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/rfi'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/rfi/rfi-s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/rfi/rfi-s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/rfi'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation/s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.xml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/annotation'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/manifest.safe',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/manifest.safe',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE'}, {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/measurement/s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.tiff',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/measurement/s1a-iw-grd-vh-20220202t154011-20220202t154040-041736-04f765-002.tiff',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/measurement'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/measurement/s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.tiff',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/measurement/s1a-iw-grd-vv-20220202t154011-20220202t154040-041736-04f765-001.tiff',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/measurement'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/icons/logo.png',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/icons/logo.png',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/icons'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/map-overlay.kml',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/map-overlay.kml',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/product-preview.html',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/product-preview.html',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/quick-look.png',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/quick-look.png',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-calibration.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-calibration.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-measurement.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-measurement.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-noise.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-noise.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-product.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-product.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-quicklook.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-quicklook.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-rfi.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-level-1-rfi.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-map-overlay.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-map-overlay.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-object-types.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-object-types.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'},
                             {
                                 'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-product-preview.xsd',
                                 'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support/s1-product-preview.xsd',
                                 'path': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/support'}],
                        'sensor': 'sar-c',
                        'uid': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/',
                        'format': 'SAFE', 'pass_direction': 'ascending', 'boundary': {'type': 'Polygon',
                                                                                      'coordinates': [
                                                                                          [[27.646376, 59.761978],
                                                                                           [32.151646, 60.183868],
                                                                                           [32.67691, 58.452579],
                                                                                           [28.390108, 58.038574]]]},
                        'quicklook': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/quick-look.png'}]

        mongoclient.return_value.sat_db.files.find.return_value = find_result

        req_dict = {'type': 'FeatureCollection', 'features': [], 'sourceID': 'mongo',
                    'start_time': '2022-02-02T11:52:00.000Z', 'end_time': '2022-02-04T11:52:00.000Z'}
        rv = client.post('/search', data=json.dumps(req_dict), content_type='application/json')
        assert rv.status_code == 200
        res = json.loads(rv.data)
        assert res == {'features': [{'geometry': {'coordinates': [
            [[27.646376, 59.761978], [32.151646, 60.183868], [32.67691, 58.452579], [28.390108, 58.038574]]],
                                                  'type': 'Polygon'}, 'properties': {
            'id': 'S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/',
            'pass_direction': 'ascending',
            'quicklook': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/preview/quick-look.png',
            'uri': '/satnfs/polar_in/sentinel1/sar-c/lvl1/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE/S1A_IW_GRDH_1SDV_20220202T154011_20220202T154040_041736_04F765_E57A.SAFE-report-20220202T164128.pdf'},
                                     'type': 'Feature'}]}


    def teardown(self):
        shutil.rmtree(self.tiffdir)
        shutil.rmtree(self.safedir)



