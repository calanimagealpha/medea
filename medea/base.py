from functools import singledispatch

from sqlalchemy.ext.declarative import declarative_base

from medea import schema

class Base:
    """Provide common serialization help."""

    # (spec property -> callable(value -> serialized value))
    __serialization__ = {}

    def to_dict(self, as_model_dict=False):
        """Convert the model instance to a dict based on the keys defined for the model in schema.
        No validation is performed on the types expected of the attributes from the schema.
        """

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
                # First stop: completely synthetic serialization
                # These are called with no argument
                if spec_key in self.__serialization__:
                    result[spec_key] = self.__serialization__[spec_key]()
                    continue
                else:
                    raise ValueError('Spec defines property {} which is not present on the model'.format(model_key))

            attr_val = getattr(self, model_key)

            # None attributes = don't include
            if attr_val:
                if model_key in self.__serialization__:
                    result[spec_key] = self.__serialization__[spec_key](attr_val)
                else:
                    result[spec_key] = prepare(attr_val)

        if as_model_dict:
            result = api_to_model_dict({cls_name: result})

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


def api_to_model_dict(api_dict):
    """Converts a dict with keys defined in the schema to a dict with keys matching
    the model columns"""
    wrapping_key, = api_dict.keys()
    spec_name = schema.wrapping_key_to_spec[wrapping_key.lower()]
    api_data = api_dict[wrapping_key]
    definitions = schema.spec.spec_dict['definitions']

    spec_to_model_keys = {
        key: schema.spec_to_model_attribute(key)
        for key
        in definitions[spec_name]['properties'].keys()
    }

    model_dict = {}
    for spec_key, model_key in spec_to_model_keys.items():
        if spec_key in api_data:
            model_dict[model_key] = api_data[spec_key]
    return model_dict
