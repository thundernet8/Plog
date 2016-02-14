# coding=utf-8

from flask import request
from flask import jsonify
from flask.ext.login import login_user

from . import api
from .errors import value_error
from .errors import action_failed
from app.core.models.users import User


@api.route('/login', methods=['POST'])
def login():
    """
    登录 api 接口
    :return: 结果 json
    """
    # POST username/password
    username = request.form.get('username')  # TODO 可采用邮箱登录
    password = request.form.get('password')
    # print(request.form)
    if not username or not password:
        # parameters are invalid
        return value_error(u"无效的用户名或密码")
    try:
        user = User(name=username)
        if user and user.verify_password(password):
            # login_manager 保存登录状态
            login_user(user, remember=True)  # TODO 可让用户选择是否保存登录状态
            # ajax response
            response = jsonify({'success': 1, 'message': u'登录成功'})
            response.status_code = 200
            return response
        else:
            return value_error(u"用户名或密码错误")
    except:
        return action_failed(u'查找用户失败')
