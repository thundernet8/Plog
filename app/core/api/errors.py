from flask import jsonify

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


@api.errorhandler(ValueError)
def value_error_handler(e):
    return value_error(e.args[0])


@api.errorhandler(ValidationError)
def validate_error_handler(e):
    return validate_error(e.args[0])
