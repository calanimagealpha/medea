import datetime
import pytest
import simplejson

from medea import app
from medea.base import api_to_model_dict
from medea.db_operations import session_scope

@pytest.yield_fixture
def test_client():
    app.app.config['TESTING'] = True
    yield app.app.test_client()
    app.app.config['TESTING'] = False


class TestAPIBase(object):
    mock_work_request_object = {
        'work': {
            'id': 1,
            'type': 'comic',
            'title': 'pooop',
            'catalogNumber': '1234',
            'description': 'taser',
            'creators': [],
            'tags': [],
            'isActive': False,
        }
    }
    mock_creator_request_object = {
        'creator': {
            'id': 1,
            'name': 'Miki Naoki',
            'aliases': ['Mii-kun', 'boy'],
            'isGroup': False,
        }
    }

    def assert_response_ok(self, response):
        assert getattr(response, 'status_code', None) in (200, 201)

class TestWorks(TestAPIBase):
    def test_post_works(self, use_test_db, test_client):
        response = test_client.post(
            '/api/v1/works',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_work_request_object),
        )
        self.assert_response_ok(response)

    def test_put_works(self, use_test_db, test_client):
        response = test_client.post(
            '/api/v1/works',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_work_request_object),
        )
        self.assert_response_ok(response)

        new_work_id = simplejson.loads(response.data)['work']['id']
        update_dict = dict(self.mock_work_request_object)
        new_name = 'Moomin'
        update_dict['work']['title'] = new_name
        response = test_client.put(
            '/api/v1/works/{0}'.format(new_work_id),
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(update_dict),
        )
        self.assert_response_ok(response)

        updated_work = simplejson.loads(response.data)['work']
        assert new_name == updated_work['title']
        assert new_work_id == updated_work['id']

    def test_get_works(self, use_test_db, test_client):
        post_response = test_client.post(
            '/api/v1/works',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_work_request_object),
        )
        self.assert_response_ok(post_response)
        post_work = simplejson.loads(post_response.data)
        work_id = post_work['work']['id']

        get_response = test_client.get(
            'api/v1/works/{0}'.format(work_id),
            headers={'Content-Type': 'application/json'},
        )
        self.assert_response_ok(get_response)
        get_work = simplejson.loads(get_response.data)
        assert post_work == get_work

    def test_delete_works(self, use_test_db, test_client):
        post_response = test_client.post(
            '/api/v1/works',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_work_request_object),
        )
        self.assert_response_ok(post_response)
        post_work = simplejson.loads(post_response.data)
        work_id = post_work['work']['id']

        delete_response = test_client.delete(
            'api/v1/works/{0}'.format(work_id),
            headers={'Content-Type': 'application/json'},
        )
        self.assert_response_ok(delete_response)

        get_response = test_client.get(
            'api/v1/works/{0}'.format(work_id),
            headers={'Content-Type': 'application/json'},
        )
        assert 404 == getattr(get_response, 'status_code', None)

class TestCreators(TestAPIBase):
    def test_post_creators(self, use_test_db, test_client):
        response = test_client.post(
            '/api/v1/creators',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_creator_request_object),
        )
        self.assert_response_ok(response)

    def test_put_creators(self, use_test_db, test_client):
        response = test_client.post(
            '/api/v1/creators',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_creator_request_object),
        )
        self.assert_response_ok(response)

        new_creator_id = simplejson.loads(response.data)['creator']['id']
        update_dict = dict(self.mock_creator_request_object)
        new_name = 'Mii'
        update_dict['creator']['name'] = new_name
        response = test_client.put(
            '/api/v1/creators/{0}'.format(new_creator_id),
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(update_dict),
        )
        self.assert_response_ok(response)

        updated_creator = simplejson.loads(response.data)['creator']
        assert new_name == updated_creator['name']
        assert new_creator_id == updated_creator['id']

    def test_get_creators(self, use_test_db, test_client):
        post_response = test_client.post(
            '/api/v1/creators',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_creator_request_object),
        )
        self.assert_response_ok(post_response)
        post_creator = simplejson.loads(post_response.data)
        creator_id = post_creator['creator']['id']

        get_response = test_client.get(
            'api/v1/creators/{0}'.format(creator_id),
            headers={'Content-Type': 'application/json'},
        )
        self.assert_response_ok(get_response)
        get_creator = simplejson.loads(get_response.data)
        assert post_creator == get_creator

    def test_delete_creators(self, use_test_db, test_client):
        post_response = test_client.post(
            '/api/v1/creators',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_creator_request_object),
        )
        self.assert_response_ok(post_response)
        post_creator = simplejson.loads(post_response.data)
        creator_id = post_creator['creator']['id']

        delete_response = test_client.delete(
            'api/v1/creators/{0}'.format(creator_id),
            headers={'Content-Type': 'application/json'},
        )
        self.assert_response_ok(delete_response)

        get_response = test_client.get(
            'api/v1/creators/{0}'.format(creator_id),
            headers={'Content-Type': 'application/json'},
        )
        assert 404 == getattr(get_response, 'status_code', None)

