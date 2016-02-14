# coding=utf-8

from flask import render_template
from flask import redirect
from flask.ext.login import current_user

from . import auth
from app.core.models.settings import Setting


@auth.route('/login.do')
def login():
    """ 登录页面 """
    if current_user.is_logged_in:
        return redirect('main.index')
    return render_template('auth/login.html', Setting=Setting)


@auth.route('/register.do')
def register():
    """" 注册页面 """
    if current_user.is_logged_in:
        return redirect('main.index')
    return render_template('auth/register.html', Setting=Setting)


@auth.route('/findPass.do')
def find_pass():
    """ 找回密码页面 """
    return 'blank'
    pass  # TODO


@auth.route('/confirmEmail.do')
def confirm_email():
    """ 确认邮箱页面 """
    return 'blank'
    pass  # TODO
