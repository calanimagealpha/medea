from functools import singledispatch

from sqlalchemy import (Column, Boolean, Integer, String, DateTime, Enum, ForeignKey, Table)
from sqlalchemy import or_
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import Comparator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty

from medea import schema

class Base:
    def to_dict(self):
        """Convert the model instance to a dict based on the keys defined for the model in schema.
        No validation is performed on the types expected of the attributes from the schema.
        """

        # TODO: Serialization overrides

        cls_name = type(self).__name__
        definitions = schema.spec.spec_dict['definitions']

        if cls_name not in definitions:
            raise ValueError('No corresponding spec definition for {}'.format(cls_name))

        spec_to_model_keys = {
            key: schema.spec_to_model_attribute(key)
            for key
            in definitions[cls_name]['properties'].keys()
        }

        result = {}
        for spec_key, model_key in spec_to_model_keys.items():
            # Do we have this attribute?
            if not hasattr(self, model_key):
                raise ValueError('Spec defines property {} which is not present on the model'.format(model_key))

            attr_val = getattr(self, model_key)

            # None attributes = don't include
            if attr_val:
                result[spec_key] = prepare(attr_val)

        return result

Base = declarative_base(cls=Base)

@singledispatch
def prepare(val):
    return val

@prepare.register(Base)
def prepare_orm(val):
    return val.id

@prepare.register(list)
def prepare_orm_many(val):
    return [item.id for item in val]

creator_related_creators_association_table = Table('creator_related_creators', Base.metadata,
    Column('left_creator_id', Integer, ForeignKey('creator.id'), primary_key=True),
    Column('right_creator_id', Integer, ForeignKey('creator.id'), primary_key=True),
)

creator_tags_association_table = Table('creator_tags', Base.metadata,
    Column('work_id', Integer, ForeignKey('work.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tag.id'), primary_key=True),
)

workpart_work_creators_association_table = Table('workpart_work_creators', Base.metadata,
    Column('workpart_id', Integer, ForeignKey('workpart.id'), primary_key=True),
    Column('work_creator_association_id', Integer, ForeignKey('work_creators.id'), primary_key=True)
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
    type = Column('type', Enum('music', 'video', 'game', 'comic', 'artbook', 'photobook'))
    catalog_number = Column('catalog_number', String)
    release_date = Column('release_date', DateTime)
    tags = relationship(
        'Tag',
        secondary=creator_tags_association_table,
        backref='works'
    )
    description = Column('description', String)
    path = Column('path', String)
    is_active = Column('is_active', Boolean)

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
    __tablename__ = 'workpart'

    id = Column(Integer, primary_key=True)

    work_id = Column('work_id', Integer, ForeignKey('work.id'))
    work = relationship('Work', backref='parts')
    work_creators_associations = relationship(
        'WorkCreatorAssociation',
        secondary=workpart_work_creators_association_table,
    )
    major_number = Column('major_number', Integer)
    minor_number = Column('minor_number', Integer)
    title = Column('title', String)
    length = Column('length', Integer)

