from flask import Blueprint
from flask import g
from flask import request
from flask.ext.httpauth import HTTPBasicAuth

api = Blueprint('api', __name__)
auth = HTTPBasicAuth()

from . import register
from . import errors
from . import login
from . import article
from . import token
from . import tag
from . import post
from .errors import unauthorized
from .errors import invalid_request
from app.core.models.users import User
from app.core.models.users import AnonymousUser


@auth.verify_password
def verify_password(username, password):
    authorization = request.headers.get('Authorization', '').split(' ')
    bearer = authorization[1] if len(authorization) > 1 else ''
    if bearer:
        g.current_user = User.verify_access_token(bearer)
        g.token_used = True
        return g.current_user is not None
    if username == '':
        g.current_user = AnonymousUser()
        return True
    user = User(username=username)
    if not user or not user.user_id:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def handle_error():
    return unauthorized(message='access token expired or invalid or username and password dose not match'), 401

