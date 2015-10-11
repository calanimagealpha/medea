from sqlalchemy import (Column, Boolean, Integer, String,
    DateTime, ForeignKey, Table)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy import or_

Base = declarative_base()

creator_related_creators_association_table = Table('creator_related_creators', Base.metadata,
    Column('left_creator_id', Integer, ForeignKey('creator.id'), primary_key=True),
    Column('right_creator_id', Integer, ForeignKey('creator.id'), primary_key=True),
)

creator_tags_association_table = Table('creator_tags', Base.metadata,
    Column('work_id', Integer, ForeignKey('work.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True),
)

workpart_creators_association_table = Table('workpart_creators', Base.metadata,
    Column('workpart_id', Integer, ForeignKey('workpart.id'), primary_key=True),
    Column('creator_id', Integer, ForeignKey('creator.id'), primary_key=True)
)

class WorkCreatorAssociation(Base):
    __tablename__ = 'work_creators'

    id = Column(Integer, primary_key=True)

    work_id = Column('work_id', Integer, ForeignKey('work.id'))
    work = relationship('Work', backref='creators')
    creator_id = Column('creator_id', Integer, ForeignKey('creator.id'))
    creator = relationship('Creator', backref='works')
    role = Column('role', String)

    def __init__(self, work=None, creator=None, role=None):
        self.work = work
        self.creator = creator
        self.role = role

class Work(Base):
    __tablename__ = 'work'

    id = Column(Integer, primary_key=True)
    title = Column('title', String)
    catalog_number = Column('catalog_number', String)
    release_date = Column('release_date', DateTime)
    release_event = Column('release_event', String)
    tags = relationship(
        'Tag',
        secondary=creator_tags_association_table,
        backref='works'
    )
    description = Column('description', String)
    is_group = Column('is_group', Boolean)

class Creator(Base):
    __tablename__ = 'creator'

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

    @hybrid_property
    def related_creators(self):
        return self.related_creators_forward + self.related_creators_back

    @related_creators.setter
    def related_creators(self, related_creators):
        self.related_creators_forward = related_creators

    @related_creators.comparator
    def related_creators(cls):
        return RelatedCreatorComparator(
            cls.related_creators_forward,
            cls.related_creators_back,
        )


class RelatedCreatorComparator(Comparator):
    def __init__(self, *args):
        self.underlying_associations = args

    def operate(self, op, *args, **kwargs):
        return or_(*[
            op(association, *args, **kwargs)
            for association
            in self.underlying_associations
        ])


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    value = Column('value', String)
    description = Column('description', String)

class WorkPart(Base):
    __tablename__ = 'workpart'

    id = Column(Integer, primary_key=True)

    work_id = Column('work_id', Integer, ForeignKey('work.id'))
    work = relationship('Work', backref='parts')
    creator_associations = relationship(
        'Creator',
        secondary=workpart_creators_association_table
    )
    major_number = Column('major_number', Integer)
    minor_number = Column('minor_number', Integer)
    title = Column('title', String)
    length = Column('length', Integer)

