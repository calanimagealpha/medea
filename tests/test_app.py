import datetime
import pytest
import simplejson

from medea import app

@pytest.yield_fixture
def test_client():
    yield app.app.test_client()


class TestAPIBase(object):
    mock_work_request_object = {
        'Work': {
            'id': 1,
            'type': 'comic',
            'title': 'pooop',
            'catalogNumber': '1234',
            'releaseDate': None,
            'description': 'taser',
            'creators': [],
            'tags': [],
            'isActive': False,
        }
    }

    mock_creator_request_object = {}

    def assert_response_ok(self, response):
        assert getattr(response, 'status_code', None) in (200, 201)

class TestWorks(TestAPIBase):
    def test_add_works(self, use_test_db, test_client):
        response = test_client.post(
            '/api/v1/works',
            headers={'Content-Type': 'application/json'},
            data=simplejson.dumps(self.mock_work_request_object),
        )
        self.assert_response_ok(response)
