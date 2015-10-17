import datetime
import pytest
import testing_utils

from  medea import logic
from medea.db_operations import session_scope
from medea.models import Work, Creator, Tag, WorkPart

@pytest.yield_fixture
def test_work_dict():
    work_dict = {
        'id': 1,
        'type': 'comic',
        'title': 'pooop',
        'catalog_number': '1234',
        'release_date': datetime.datetime.today(),
        'description': 'taser',
        'roles': [],
        'tags': [],
        'is_active': False,
    }
    yield work_dict

def test_create_work(use_test_db, test_work_dict):
    new_test_work = logic.create_work(test_work_dict)
    assert new_test_work['title'] == 'pooop'

def test_create_work_with_roles(use_test_db, test_work_dict):
    with session_scope() as session:
        test_creator = Creator()
        session.add(test_creator)
        session.flush()
        test_creator_id = test_creator.id
        roles = {'illustrator': [test_creator_id]}
    test_work_dict['roles'] = roles
    new_test_work = logic.create_work(test_work_dict)
    assert new_test_work['roles'] == [test_creator_id]

def test_update_work_with_roles(use_test_db, test_work_dict):
    new_test_work = logic.create_work(test_work_dict)
    with session_scope() as session:
        test_creator = Creator()
        session.add(test_creator)
        session.flush()
        test_creator_id = test_creator.id
        roles = {'illustrator': [test_creator_id]}
    test_work_dict['roles'] = roles
    updated_test_work = logic.update_work(test_work_dict)
    assert new_test_work['id'] == updated_test_work['id']
    assert updated_test_work['roles'] == [test_creator_id]
