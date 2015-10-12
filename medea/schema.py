import re
from functools import partial
import simplejson
from bravado_core.spec import Spec

SCHEMA_PATH = 'swagger.json'

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
