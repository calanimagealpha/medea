import datetime
import pytest
import testing_utils

from medea import logic
from medea.db_operations import session_scope
from medea.models import Work, Creator, Role, Tag, WorkPart

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
    test_creator_id = testing_utils.create_fake_creator()['id']
    test_work_dict['roles'] = {'illustrator': [test_creator_id]}
    new_test_work = logic.create_work(test_work_dict)
    with session_scope() as session:
        created_role_id = session.query(Role)\
            .filter_by(work_id=new_test_work['id'], creator_id=test_creator_id)\
            .first().id
    assert new_test_work['roles'] == [created_role_id]

def test_update_work_with_roles(use_test_db, test_work_dict):
    new_test_work = logic.create_work(test_work_dict)
    test_creator_id = testing_utils.create_fake_creator()['id']
    test_work_dict['roles'] = {'illustrator': [test_creator_id]}
    updated_test_work = logic.update_work(test_work_dict['id'], test_work_dict)
    assert new_test_work['id'] == updated_test_work['id']
    assert updated_test_work['roles'] == [test_creator_id]

@pytest.yield_fixture
def test_creator_dict():
    creator_dict = {
        'name': 'Jean Valjean',
        'aliases': ['24601', 'rarepepe'],
        'roles': [],
    }
    yield creator_dict

def test_create_creator(use_test_db, test_creator_dict):
    new_test_creator = logic.create_creator(test_creator_dict)
    assert new_test_creator['name'] == test_creator_dict['name']
    assert test_creator_dict['aliases'][0] in new_test_creator['aliases']

def test_create_creator_with_roles(use_test_db, test_creator_dict):
    test_work_id = testing_utils.create_fake_work()['id']
    test_creator_dict['roles'] = {'illustrator': [test_work_id]}
    new_test_creator = logic.create_creator(test_creator_dict)
    with session_scope() as session:
        created_role_id = session.query(Role)\
            .filter_by(work_id=test_work_id, creator_id=new_test_creator['id'])\
            .first().id
    assert new_test_creator['roles'] == [created_role_id]

def test_update_creator_with_roles(use_test_db, test_creator_dict):
    test_creator_id = testing_utils.create_fake_creator()['id']
    test_work_id = testing_utils.create_fake_work()['id']
    test_creator_dict['roles'] = {'illustrator': [test_work_id], 'author': [test_work_id]}
    test_creator_dict['related_creators'] = [test_creator_id]
    new_test_creator = logic.create_creator(test_creator_dict)

    test_creator_dict['aliases'].pop()
    test_creator_dict['roles'].pop('illustrator')
    updated_test_creator = logic.update_creator(new_test_creator['id'], test_creator_dict)
    with session_scope() as session:
        created_role = session.query(Role)\
            .filter_by(work_id=test_work_id, creator_id=new_test_creator['id'])\
            .first().to_dict()
        test_work = session.query(Work).filter_by(id=test_work_id).first().to_dict()
    assert test_work['roles'] == updated_test_creator['roles']
    assert test_creator_dict['aliases'] == updated_test_creator['aliases']
    assert 'author' == created_role['role']
