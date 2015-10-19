from sqlalchemy import func

from medea.models import Work, Creator, CreatorAlias, Tag, WorkPart, Role
from medea.db_operations import session_scope


def create_work(work_dict):
    work_dict = dict(work_dict)
    work_dict.pop('id', None)
    with session_scope() as session:
        roles = work_dict.pop('roles', None)
        tags = work_dict.pop('tags', None)
        new_work = Work(**work_dict)
        session.add(new_work)
        if roles:
            _update_roles_for_work(session, roles, new_work)
        if tags:
            #TODO: Add tags
            pass
        session.commit()
        return new_work.to_dict()

def update_work(work_id, work_dict):
    work_dict = dict(work_dict)
    work_dict.pop('id', None)
    with session_scope() as session:
        work = session.query(Work).filter_by(id=work_id).first()
        if not work:
            return
        roles = work_dict.pop('roles', None)
        tags = work_dict.pop('tags', None)
        if roles:
            _update_roles_for_work(session, roles, work)
        if tags:
            #TODO: Add tags
            pass
        for field, value in work_dict.items():
            setattr(work, field, value)
        session.commit()
        return work.to_dict()

def _update_roles_for_work(session, roles, work):
    if isinstance(roles, list):
        return _update_roles_for_model_from_list(session, roles, work)
    elif isinstance(roles, dict):
        return _update_roles_for_work_from_dict(session, roles, work)

def _update_roles_for_work_from_dict(session, roles, work):
    """Creates the roles for a work when given a role dict:
    {'some role': [1, 2], 'other role': [3]} where the integers are IDs of creators"""
    updated_roles = []
    for role, creator_ids in roles.items():
        for creator_id in creator_ids:
            existing_role = _get_role_from_role_and_ids(session, role, creator_id, work.id)
            if existing_role:
                updated_roles.append(existing_role.id)
                continue
            creator = session.query(Creator).filter_by(id=creator_id).first()
            if creator:
                new_role = Role(work=work, creator=creator, role=role)
                session.commit()
                updated_roles.append(new_role.id)
    session.query(Role).filter(~Role.id.in_(updated_roles)).delete(synchronize_session='fetch')

def create_creator(creator_dict):
    creator_dict = dict(creator_dict)
    creator_dict.pop('id', None)
    with session_scope() as session:
        roles = creator_dict.pop('roles', None)
        related_creators = creator_dict.pop('related_creators', [])
        aliases = creator_dict.pop('aliases', [])
        new_creator = Creator(**creator_dict)
        session.add(new_creator)
        if roles:
            _update_roles_for_creator(session, roles, new_creator)
        if related_creators:
            related_creator_rows = session.query(Creator)\
                .filter(Creator.id.in_(related_creators))\
                .all()
            new_creator.related_creators = related_creator_rows
        if aliases:
            _update_creator_aliases(session, aliases, new_creator)
        session.commit()
        return new_creator.to_dict()

def update_creator(creator_id, creator_dict):
    creator_dict = dict(creator_dict)
    creator_dict.pop('id', None)
    with session_scope() as session:
        creator = session.query(Creator).filter_by(id=creator_id).first()
        if not creator:
            return
        roles = creator_dict.pop('roles', None)
        related_creators = creator_dict.pop('related_creators', [])
        aliases = creator_dict.pop('aliases', [])
        if roles:
            _update_roles_for_creator(session, roles, creator)
        if related_creators:
            related_creator_rows = session.query(Creator)\
                .filter(Creator.id.in_(related_creators))\
                .all()
            creator.related_creators = related_creator_rows
        if aliases:
            _update_creator_aliases(session, aliases, creator)
        for field, value in creator_dict.items():
            setattr(creator, field, value)
        session.commit()
        return creator.to_dict()

def _update_roles_for_creator(session, roles, creator):
    if isinstance(roles, list):
        _update_roles_for_model_from_list(session, roles, creator)
    elif isinstance(roles, dict):
        _update_roles_for_creator_from_dict(session, roles, creator)

def _update_roles_for_creator_from_dict(session, roles, creator):
    """Creates the roles for a creator when given a role dict:
    {'some role': [1, 2], 'other role': [3]} where the integers are IDs of works"""
    updated_roles = []
    for role, work_ids in roles.items():
        for work_id in work_ids:
            existing_role = _get_role_from_role_and_ids(session, role, creator.id, work_id)
            if existing_role:
                updated_roles.append(existing_role.id)
                continue
            work = session.query(Work).filter_by(id=work_id).first()
            if work:
                new_role = Role(work=work, creator=creator, role=role)
                session.commit()
                updated_roles.append(new_role.id)
    session.query(Role).filter(~Role.id.in_(updated_roles)).delete(synchronize_session='fetch')


def _update_creator_aliases(session, aliases, creator):
    updated_aliases = []
    for alias in aliases:
        existing_alias = session.query(CreatorAlias).filter_by(creator_id=creator.id, name=alias).first()
        if existing_alias:
            updated_aliases.append(existing_alias.id)
            continue
        new_alias = CreatorAlias(name=alias, creator=creator)
        session.commit()
        updated_aliases.append(new_alias.id)
    session.query(CreatorAlias).filter(~CreatorAlias.id.in_(updated_aliases)).delete(synchronize_session='fetch')

def _update_roles_for_model_from_list(session, roles, model_instance):
    #TODO: Add this when roles and creators are done
    pass

def _get_role_from_role_and_ids(session, role, creator_id, work_id):
    role_result = session.query(Role).filter_by(
        creator_id=creator_id,
        work_id=work_id,
        role=role
    )\
    .first()
    return role_result


