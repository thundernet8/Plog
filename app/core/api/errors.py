from flask import jsonify
from flask import url_for

from . import api
from app.core.models.exceptions import ValidationError


def value_error(message):
    response = jsonify({'error': 'invalid value', 'message': message})
    response.status_code = 200
    return response


def validate_error(message):
    response = jsonify({'error': 'validation failed', 'message': message})
    # response.status_code = 400
    response.status_code = 200
    return response


def action_failed(message):
    response = jsonify({'error': 'action failed', 'message': message})
    response.status_code = 200
    return response


def unauthorized(message):
    message = message or 'invalid credential'
    response = jsonify({'error': 'unauthorized', 'message': message, 'grant_token':
        url_for('api.grant_token', _external=True), 'refresh_token': url_for('api.refresh_token', _external=True)})
    response.status_code = 401
    return response


def invalid_request(message):
    message = message or 'your request path is incorrect'
    response = jsonify({'error': 'invalid request', 'message': message})
    response.status_code = 404
    return response


@api.errorhandler(ValueError)
def value_error_handler(e):
    return value_error(e.args[0])


@api.errorhandler(ValidationError)
def validate_error_handler(e):
    return validate_error(e.args[0])
