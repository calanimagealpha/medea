from medea import models
from medea.db_operations import session_scope

from sqlalchemy import create_engine



def test_poop(use_test_db):
    with session_scope() as poop_session:
        poop_work = models.Work(title='poop')
        poop_creator_1 = models.Creator(name='creapoop1')
        poop_work_creator_ass = models.WorkCreatorAssociation(
             poop_work,
             poop_creator_1,
             'rectum',
        )
        poop_work.creators = [poop_work_creator_ass]
        poop_creator_2 = models.Creator(name='creapoop2')
        poop_creator_1.related_creators = [poop_creator_2]
        poop_session.add(poop_creator_1)
        poop_session.add(poop_work)


