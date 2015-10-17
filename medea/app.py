import simplejson

from flask import Flask, request, jsonify
from flask.ext.cors import CORS
from werkzeug.exceptions import default_exceptions, HTTPException

from medea.base import api_to_model_dict
from medea import logic

__all__ = ['json_app']

def json_app(import_name, **kwargs):
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
        return response

    app = Flask(import_name, **kwargs)
    for code in default_exceptions.keys():
        app.error_handler_spec[None][code] = make_json_error
    return app


app = json_app(__name__)
CORS(app)

@app.route('/api/v1/works', methods=['POST', 'PUT'])
def works():
    request_data = simplejson.loads(request.data)
    model_data = api_to_model_dict(request_data)
    if request.method == 'POST':
        response = logic.create_work(model_data)
        return jsonify(response)
    elif request.method == 'PUT':
        response = logic.update_work(model_data)
        return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
