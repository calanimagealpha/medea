import builtins

import mock
import pytest
import yaml
from mock import mock_open
from sqlalchemy import create_engine

from medea import models
from medea.db_operations import Session


@pytest.fixture
def use_test_db():
    engine = create_engine('sqlite://')
    models.Base.metadata.create_all(engine)
    Session.configure(bind=engine)

@pytest.yield_fixture(autouse=True)
def use_testing_config():
    testing_config = yaml.load(open('config.yaml.test'))
    with mock.patch.object(builtins, 'open', mock_open(read_data='')):
        from medea import config
    with mock.patch.object(config, 'config_path',  'config.yaml.test'),\
        mock.patch('medea.app.config', return_value=testing_config):
        yield 
