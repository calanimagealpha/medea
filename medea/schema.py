import re
from functools import partial

import simplejson
from bravado_core.spec import Spec
from bravado_core import response

# TODO: How to locate this file in the right way?
SCHEMA_PATH = 'swagger.json'

__all__ = (
    'spec',
    'model_to_spec_attribute',
    'spec_to_model_attribute',
    'rule_to_path',
    'validate_model_dict',
    'validate_response_dict',
)

spec_dict = simplejson.load(open(SCHEMA_PATH))

spec = Spec.from_dict(spec_dict)

model_to_spec_attribute = partial(
    re.sub,
    r'_([a-z])',
    lambda s: s.group(1).upper(),
)

spec_to_model_attribute = partial(
    re.sub,
    r'[A-Z]',
    lambda s: r'_' + s.group(0).lower(),
)

# Convert a Flask route rule to a Swagger path
rule_to_path = partial(
    re.sub,
    r'/<(?:.*:)(.*)>(/?)',
    lambda s: r'/{{{0}}}{1}'.format(model_to_spec_attribute(s.group(1)), s.group(2)),
)

def validate_model_dict(model_dict):
    raise NotImplementedError

class Response(response.OutgoingResponse):
    content_type = 'application/json'

    def __init__(self, response_dict, headers):
        self.headers = headers
        self.text = response_dict

    def json(self):
        # TODO: Does validate_schema_object work okay with dicts?
        return self.text

def validate_response_dict(path, response_dict, http_method='GET', status_code=200, headers=None):
    if not headers:
        headers = {}

    response = Response(response_dict, headers)

    # TODO: munge Flask routes to Swagger paths
    op = spec.get_op_for_request(http_method, path)
    response_spec = response.get_response_spec(status_code, op)

    response.validate_response(response_spec, op, response)
