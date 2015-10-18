from functools import wraps
import traceback

from flask import Flask, request, jsonify
from flask.ext.cors import CORS
from werkzeug.exceptions import default_exceptions, HTTPException

from medea import logic
from medea import models
from medea.base import api_to_model_dict
from medea.schema import rule_to_path

from medea.db_operations import Session
from medea.db_operations import session_scope
from sqlalchemy import create_engine

__all__ = ['json_app']

def medea_app(import_name, **kwargs):
    def make_json_error(ex):
        response = jsonify(message=str(ex))
        response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
        traceback.print_exc()
        return response

    app = Flask(import_name, **kwargs)
    for code in default_exceptions.keys():
        app.error_handler_spec[None][code] = make_json_error

    CORS(app)
    return app


app = medea_app(__name__)

def json_endpoint(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        # swagger_path = rule_to_path(request.url_rule.rule)
        # TODO: Request validation
        response = func(*args, **kwargs)
        # TODO: Response validation

        if isinstance(response, tuple):
            return response

        return jsonify(response)
    return wrapped


@app.route('/api/v1/works', methods=['POST', 'PUT'])
@json_endpoint
def works():
    request_data = request.get_json()
    print(request_data)
    model_data = api_to_model_dict(request_data)
    if request.method == 'POST':
        response = logic.create_work(model_data)
        return response
    elif request.method == 'PUT':
        response = logic.update_work(model_data)
        return response

@app.route('/api/v1/works/<int:work_id>')
@json_endpoint
def work(work_id):

    work = None
    with session_scope() as session:
        work = session.query(models.Work).filter_by(id=work_id).scalar()

    if work:
        return {'work': work.to_dict()}

    return {}, 404

if __name__ == "__main__":
    # TODO: remove
    engine = create_engine('sqlite:///medea.db')
    Session.configure(bind=engine)

    app.run(host='0.0.0.0')
