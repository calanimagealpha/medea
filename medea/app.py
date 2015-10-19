from functools import wraps
import traceback

from flask import Flask, request, jsonify
from flask.ext.cors import CORS
from werkzeug.exceptions import default_exceptions, HTTPException

from medea import logic
from medea import models
from medea.base import api_to_model_dict
from medea.config import config
from medea.schema import validate_request
from medea.schema import validate_response_dict

from medea.db_operations import Session
from medea.db_operations import session_scope
from sqlalchemy import create_engine

__all__ = ['medea_app']

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
        # TODO: Request validation
        if config['validate_requests']:
            validate_request(request)

        response = func(*args, **kwargs)

        if isinstance(response, tuple):
            response_body, status_code = response
        else:
            response_body, status_code = response, 200

        if config['validate_responses']:
            validate_response_dict(request.url_rule.rule, response_body, http_method=request.method, status_code=status_code)

        return jsonify(response_body), status_code
    return wrapped


@app.route('/api/v1/works', methods=['POST'])
@json_endpoint
def works():
    model_data = api_to_model_dict(request.get_json())
    response = logic.create_work(model_data)
    return {'work': response}, 201

@app.route('/api/v1/works/<int:work_id>', methods=['DELETE', 'GET', 'PUT'])
@json_endpoint
def works_with_id(work_id):
    response = {}
    work = None
    with session_scope() as session:
        work = session.query(models.Work).filter_by(id=work_id).scalar()
        if work:
            if request.method == 'GET':
                response = {'work': work.to_dict()}
            elif request.method == 'DELETE':
                session.query(models.Work).filter_by(id=work_id).delete()
                response = {'status': 'Delete OK'}
            elif request.method == 'PUT':
                model_data = api_to_model_dict(request.get_json())
                response = {'work': logic.update_work(work_id, model_data)}
    return response or ({}, 404)

@app.route('/api/v1/creators', methods=['POST'])
@json_endpoint
def creators():
    model_data = api_to_model_dict(request.get_json())
    response = logic.create_creator(model_data)
    return {'creator': response}, 201

@app.route('/api/v1/creators/<int:creator_id>', methods=['DELETE', 'GET', 'PUT'])
@json_endpoint
def creators_with_id(creator_id):
    response = {}
    creator = None
    with session_scope() as session:
        creator = session.query(models.Creator).filter_by(id=creator_id).scalar()
        if creator:
            if request.method == 'GET':
                 response = {'creator': creator.to_dict()}
            elif request.method == 'DELETE':
                session.query(models.Creator).filter_by(id=creator_id).delete()
                response = {'status': 'Delete OK'}
            elif request.method == 'PUT':
                model_data = api_to_model_dict(request.get_json())
                response = {'creator': logic.update_creator(creator_id, model_data)}
    return response or ({}, 404)


if __name__ == "__main__":
    # TODO: remove
    engine = create_engine('sqlite:///medea.db')
    Session.configure(bind=engine)

    app.run(host='0.0.0.0')
