from sqlalchemy import (Column, Boolean, Integer, String, DateTime, Enum, ForeignKey, Table)
from sqlalchemy import or_
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from medea.base import Base

creator_related_creators_association_table = Table('creator_related_creators', Base.metadata,
    Column('left_creator_id', Integer, ForeignKey('creator.id'), primary_key=True),
    Column('right_creator_id', Integer, ForeignKey('creator.id'), primary_key=True),
)

work_tags_association_table = Table('work_tags', Base.metadata,
    Column('work_id', Integer, ForeignKey('work.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True),
)

work_part_roles_association_table = Table('work_part_roles', Base.metadata,
    Column('work_part_id', Integer, ForeignKey('work_part.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('role.id'), primary_key=True)
)

class Role(Base):
    __tablename__ = 'role'

    id = Column(Integer, primary_key=True)

    work_id = Column('work_id', Integer, ForeignKey('work.id'))
    work = relationship('Work', backref='roles')
    creator_id = Column('creator_id', Integer, ForeignKey('creator.id'))
    creator = relationship('Creator', backref='roles')
    role = Column('role', String)

    def __init__(self, work=None, creator=None, role=None):
        self.work = work
        self.creator = creator
        self.role = role

class Work(Base):
    __tablename__ = 'work'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    type = Column('type', Enum('music', 'video', 'game', 'comic', 'artbook', 'photobook'))
    catalog_number = Column('catalog_number', String)
    release_date = Column('release_date', DateTime)
    tags = relationship(
        'Tag',
        secondary=work_tags_association_table,
        backref='works'
    )
    description = Column('description', String)
    path = Column('path', String)
    is_active = Column('is_active', Boolean)

class Creator(Base):
    __tablename__ = 'creator'

    __serialization__ = {
        'aliases': lambda creator_aliases: [alias.name for alias in creator_aliases],
    }

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    related_creators_forward = relationship(
        'Creator',
        secondary=creator_related_creators_association_table,
        primaryjoin=id==creator_related_creators_association_table.c.left_creator_id,
        secondaryjoin=id==creator_related_creators_association_table.c.right_creator_id,
        backref='related_creators_back'
    )
    is_group = Column('is_group', Boolean)

    class RelatedCreatorComparator(Comparator):
        def __init__(self, *args):
            self.underlying_associations = args

        def operate(self, op, *args, **kwargs):
            return or_(*[
                op(association, *args, **kwargs)
                for association
                in self.underlying_associations
            ])

    @hybrid_property
    def related_creators(self):
        return self.related_creators_forward + self.related_creators_back

    @related_creators.setter
    def related_creators(self, related_creators):
        self.related_creators_forward = related_creators

    @related_creators.comparator
    def related_creators(cls):
        return Creator.RelatedCreatorComparator(
            cls.related_creators_forward,
            cls.related_creators_back,
        )


class CreatorAlias(Base):
    __tablename__ = 'creator_alias'

    id = Column(Integer, primary_key=True)
    name = Column('name', String)
    creator_id = Column('creator_id', Integer, ForeignKey('creator.id'))
    creator = relationship('Creator', backref='aliases')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    value = Column('value', String)
    description = Column('description', String)

class WorkPart(Base):
    __tablename__ = 'work_part'

    id = Column(Integer, primary_key=True)

    work_id = Column('work_id', Integer, ForeignKey('work.id'))
    work = relationship('Work', backref='work_parts')
    roles = relationship(
        'Role',
        secondary=work_part_roles_association_table,
    )
    major_number = Column('major_number', Integer)
    minor_number = Column('minor_number', Integer)
    title = Column('title', String)
    length = Column('length', Integer)

