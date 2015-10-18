import mock
import yaml

from medea import models
from medea.db_operations import Session

import pytest
from sqlalchemy import create_engine

@pytest.fixture
def use_test_db():
    engine = create_engine('sqlite://')
    models.Base.metadata.create_all(engine)
    Session.configure(bind=engine)

@pytest.yield_fixture(autouse=True)
def use_testing_config():
    testing_config = yaml.load(open('config.yaml.test'))
    with mock.patch.object(yaml, 'load', return_value=testing_config):
        yield 
