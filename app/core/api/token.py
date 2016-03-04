# coding=utf-8

from flask import request
from flask import jsonify
from flask import url_for

from . import api
from .errors import value_error
from .errors import action_failed
from app.core.models.users import User


@api.route('/authentication/refresh', methods=['GET', 'POST'])
def refresh_token():
    refresh = request.form.get('refresh_token') or request.args.get('refresh_token')
    new_token = User.refresh_access_token(refresh)
    if new_token and isinstance(new_token, dict):
        return jsonify(new_token)
    return jsonify({'grant_token': url_for('api.grant_token', _external=True)})


@api.route('/authentication/token', methods=['GET', 'POST'])
def grant_token():
    username = request.form.get('username') or request.args.get('username')
    password = request.form.get('password') or request.args.get('password')
    if not username or not password:
        # parameters are invalid
        return value_error(u"无效的用户名或密码")
    try:
        user = User(name=username)
        if user and user.verify_password(password):
            # ajax response
            # 生成 token
            tokens = user.generate_access_token()
            tokens.update(success=1, message=u'登录成功')
            response = jsonify(tokens)
            response.status_code = 200
            return response
        else:
            return value_error(u"用户名或密码错误")
    except:
        return action_failed(u'查找用户失败')
