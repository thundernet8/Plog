# coding=utf-8

import cgi

from flask import request
from flask import jsonify

from . import api
from app.core.models.users import User
from .errors import value_error
from .errors import action_failed
from app.core.utils.email import send_mail
from app.core.models.settings import Setting


@api.route('/register', methods=['POST'])
def register():
    """
    注册 api 接口
    :return: 结果 json
    """
    # POST username/email/password
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    if not username or not email or not password:
        # parameters are invalid
        raise value_error(u"无效的用户名,邮箱或密码")
    try:
        user = User.add_user(name=username, email=email, password=password)
        if user:
            # 异步发送邮件
            # send_mail(email, Setting.get_setting('blog_name', 'Plog')+u'注册确认邮件', 'auth/emails/register_confirm',
            #           username=username,
            #           blogname=Setting.get_setting('blog_name', 'Plog'),
            #           token=user.generate_confirmation_token())
            # ajax response
            response = jsonify({'success': 1, 'message': u'注册成功'})
            response.status_code = 200
            return response
        else:
            return value_error(u'用户名或邮箱已存在')
    except Exception, e:
        print(e)
        return action_failed(u'添加用户失败')
