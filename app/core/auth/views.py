# coding=utf-8

from flask import render_template
from flask import redirect
from flask.ext.login import current_user
from flask.ext.login import login_required
from flask import url_for
from flask import request
from flask import flash

from . import auth
from app.core.models.settings import Setting
from app.core.models.users import User
from app.core.utils.email import send_mail
from .forms import FindPassForm
from .forms import ResetPassForm


@auth.route('/login.do')
def login():
    """ 登录页面 """
    if current_user.is_logged_in:
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')


@auth.route('/register.do')
def register():
    """" 注册页面 """
    if current_user.is_logged_in:
        return redirect(url_for('main.index'))
    return render_template('auth/register.html')


@auth.route('/findPass.do', methods=['GET', 'POST'])
def find_pass():
    """ 找回密码页面 """
    form = FindPassForm()
    email = None
    if form.validate_on_submit():
        email = form.email.data
        form.email.data = ''
        user = User(email=email)
        if user and user.user_id:
            token = user.generate_reset_token(expiration=600)
            send_mail(email, Setting.get_setting('blog_name', 'Plog')+u'找回您的密码', 'auth/emails/find_pass',
                      username=user.nickname or user.name, blogname=Setting.get_setting('blog_name', 'Plog'),
                      token=token)
            message = u"我们已经发送一封密码重置邮件至您提供的邮箱, 请登录你的邮箱点击密码重置链接设置你的账户新密码"
        else:
            message = u"您提供的邮箱不存在, 请重新提交"
        return render_template('utils/pure.html', message=message)  # TODO post redirect
    return render_template('auth/find_pass.html', form=form)


@auth.route('/resetPass.do', methods=['GET', 'POST'])
def reset_pass():
    """ 重设密码页面 """
    form = ResetPassForm()
    if form.validate_on_submit():
        password = form.password.data
        form.password.data = ''
        form.password2.data = ''
        token = request.args.get('token', '')
        if User.reset_user_password(token, password):
            # TODO flask message
            flash(u'您的密码已经重设, 请使用新密码登录')
            return redirect('auth.login')
        else:
            message = u"重设密码失败, 您的链接有误或者已过期, 请重新申请"
            return render_template('utils/pure.html', message=message)  # TODO post redirect
    return render_template('auth/reset_pass.html', form=form)


@auth.route('/confirmEmail.do')
def confirm_email():
    """ 确认邮箱页面 """
    token = request.args.get('token', '')
    if token and User.confirm(token):
        message = u"邮箱验证成功, 您的账户现在已激活"
    else:
        message = u"验证失败,您的链接有误或者已过期, 请重新申请验证邮箱"
    return render_template('utils/pure.html', message=message)


@auth.route('/resendConfirmEmail.do')
@login_required
def resend_confirm_email():
    """ 重新发送请求验证邮箱邮件 """
    # 异步发送邮件
    if current_user and current_user.is_logged_in:
        send_mail(current_user.email, Setting.get_setting('blog_name', 'Plog')+u'请确认您的邮箱',
                  'auth/emails/email_reconfirm', username=current_user.nickname or current_user.name,
                  blogname=Setting.get_setting('blog_name', 'Plog'), token=current_user.generate_confirmation_token())
        message = u"我们已经重新发送一封确认邮件至您的邮箱, 请登录你的邮箱点击确认链接完成账户激活"
    else:
        message = u"请求失败, 请重新尝试, 或清除 cookie 重新登录后再进行操作"
    return render_template('utils/pure.html', message=message)
