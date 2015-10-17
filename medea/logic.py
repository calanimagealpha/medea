from sqlalchemy import func

from medea.models import Work, Creator, Tag, WorkPart, Role
from medea.db_operations import session_scope


def create_work(work_dict):
    work_dict = dict(work_dict)
    work_dict.pop('id', None)
    with session_scope() as session:
        roles = work_dict.pop('roles', None)
        tags = work_dict.pop('tags', None)
        new_work = Work(**work_dict)
        session.add(new_work)
        session.flush()
        if roles:
            _create_roles_for_work(session, roles, new_work)
        if tags:
            #TODO: Add tags
            pass
        session.flush()
        return new_work.to_dict()

def update_work(work_dict):
    work_dict = dict(work_dict)
    work_id = work_dict.pop('id')
    with session_scope() as session:
        work = session.query(Work).filter_by(id=work_id).first()
        if not work:
            return
        roles = work_dict.pop('roles', None)
        tags = work_dict.pop('tags', None)
        if roles:
            _create_roles_for_work(session, roles, work)
        if tags:
            #TODO: Add tags
            pass
        for field, value in work_dict.items():
            setattr(work, field, value)
        session.flush()
        return work.to_dict()

def _create_roles_for_work(session, roles, work):
    """Creates a list of Role instances for a work:
    {'some role': [1, 2], 'other role': [3]} where the integers are IDs of creators"""
    for role, creator_ids in roles.items():
        for creator_id in creator_ids:
            existing_role = _get_role_from_role_and_ids(session, role, creator_id, work.id)
            if existing_role:
                continue
            creator = session.query(Creator).filter_by(id=creator_id).first()
            if creator:
                new_role = Role(work=work, creator=creator, role=role) 

def _get_role_from_role_and_ids(session, role, creator_id, work_id):
    role_result = session.query(Role).filter_by(
        creator_id=creator_id,
        work_id=work_id,
        role=role
    ).first()
    return role_result
