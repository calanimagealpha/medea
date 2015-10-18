import re
from functools import partial

import simplejson
from bravado_core.spec import Spec
from bravado_core.request import IncomingRequest
from bravado_core.request import unmarshal_request
from bravado_core.response import get_response_spec
from bravado_core.response import OutgoingResponse
from bravado_core.response import validate_response
from bravado_core.validate import validate_schema_object

# TODO: How to locate this file in the right way?
SCHEMA_PATH = 'swagger.json'

__all__ = (
    'spec',
    'model_to_spec_attribute',
    'spec_to_model_attribute',
    'rule_to_path',
    'validate_model_dict',
    'validate_response_dict',
    'wrapping_key_to_spec',
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

wrapping_key_to_spec = {
    spec.lower(): spec
    for spec
    in spec.spec_dict['definitions'].keys()
}


def validate_model_dict(model_dict):
    raise NotImplementedError

class Response(OutgoingResponse):
    content_type = 'application/json'

    def __init__(self, response_dict, headers):
        self.headers = headers
        self.text = response_dict

    def json(self):
        # TODO: Does validate_schema_object work okay with dicts?
        return self.text

def validate_response_dict(rule, response_dict, http_method='GET', status_code=200, headers=None):
    path = rule_to_path(rule)

    if not headers:
        headers = {}

    # TODO: Validate the entire response, including headers
    # response = Response(response_dict, headers)

    op = spec.get_op_for_request(http_method, path)
    response_spec = get_response_spec(status_code, op)

    validate_schema_object(spec, response_spec['schema'], response_dict)

class FlaskRequestProxy(IncomingRequest):
    def __init__(self, request):
        self.path = {
            model_to_spec_attribute(key): value
            for key, value
            in request.view_args.items()
        }
        self.query = request.args
        self.form = request.form
        self.headers = request.headers

        self.json = request.get_json

def validate_request(request):
    path = rule_to_path(request.url_rule.rule)
    op = spec.get_op_for_request(request.method, path)
    request = FlaskRequestProxy(request)
    unmarshal_request(request, op)
