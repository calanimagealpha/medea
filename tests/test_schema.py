import pytest

from medea.schema import spec

HTTP_METHODS_TO_EXPECTED_RESPONSES = {
    'post': set([201]),
    'get': set([200, 404]),
    'put': set([200, 404]),
    'delete': set([200, 404]),
}

resources = [resource for resource in spec.resources.values()]

operations = [
    operation
    for resource in resources
    for operation in resource.operations.values()
]


@pytest.mark.parametrize(
    "operation",
    operations,
    ids=["{} {}".format(op.http_method.upper(), op.path_name) for op in operations]
)
def test_operation_implements_responses(operation):
    """Check that each response declares the status codes it should declare.
    """
    assert HTTP_METHODS_TO_EXPECTED_RESPONSES[operation.http_method] \
        == set([int(key) for key in operation.op_spec['responses'].keys()])


request_body_params = [
    (resource, operation, param)
    for resource in resources
    for operation in resource.operations.values()
    for param in operation.params.values()
    if param.location == 'body'
]


@pytest.mark.parametrize(
    ('resource', 'operation', 'param'),
    request_body_params,
    ids=["{} param of {} {}".format(param.name, op.http_method.upper(), op.path_name) for (_, op, param) in request_body_params],
)
def test_request_body_name_synchronization(resource, operation, param):
    """Check that each parameter transmitted in the body (nominally a wrapper key)
    is similarly named to the resource it is declared for.
    """
    # TODO: Use a real stemmer
    assert resource.name.rstrip('s') == param.name

success_responses = [
    (resource, operation, response_spec)
    for resource in resources
    for operation in resource.operations.values()
    for response_code, response_spec in operation.op_spec['responses'].items()
    if int(response_code) in range(200, 299) and operation.http_method != 'delete'
]

@pytest.mark.parametrize(
    ('resource', 'operation', 'response'),
    success_responses,
    ids=["{} {}".format(op.http_method.upper(), op.path_name) for (_, op, _) in success_responses],
)
def test_ok_response_required_and_declared_keys(resource, operation, response):
    """Check that each success status code has a wrapper key corresponding to
    the resource it is declared for marked as required and extant in properties
    except for DELETE operations.
    """
    singular_resource = resource.name.rstrip('s')

    print(singular_resource, operation.path_name, operation.http_method)
    assert singular_resource in response['schema']['required']
    assert singular_resource in response['schema']['properties'].keys()

