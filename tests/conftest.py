from medea import models
from medea.db_operations import Session

import pytest
from sqlalchemy import create_engine

@pytest.fixture
def use_test_db():
    engine = create_engine('sqlite://')
    models.Base.metadata.create_all(engine)
    Session.configure(bind=engine)

