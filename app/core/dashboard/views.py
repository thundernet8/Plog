# coding=utf-8

from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import render_template
from flask import abort
from flask.ext.login import current_user

from . import dashboard


# 验证登录
@dashboard.before_request
def before_request():
    if not current_user.is_logged_in:
        flash(u'你必须先登录才能访问控制面板')
        return redirect(url_for('auth.login', redirect=request.path))
    elif not current_user.is_editor:
        flash(u'你无权访问控制面板')
        abort(403)


# 错误处理
@dashboard.errorhandler(403)
def error_403(e):
    return render_template('error_pages/403.html')


@dashboard.errorhandler(404)
def error_404(e):
    return render_template('error_pages/404.html')


@dashboard.errorhandler(502)
def error_502(e):
    return render_template('error_pages/502.html')


# 首页
@dashboard.route('/')
def dashboard_home():
    return redirect(url_for('dashboard.all_posts'))  # TODO more


# 文章
@dashboard.route('/posts')
def posts():
    return redirect(url_for('dashboard.all_posts'))


@dashboard.route('/posts/all')
def all_posts():
    return 'all posts'


@dashboard.route('/posts/new')
def new_post():
    return 'add post'


# 标签
@dashboard.route('/tags')
def tags():
    return 'tags'


# 用户
@dashboard.route('/users')
def users():
    return redirect(url_for('dashboard.all_users'))


@dashboard.route('/users/all')
def all_users():
    return 'all users'


@dashboard.route('/users/new')
def new_user():
    return 'add user'


@dashboard.route('/users/edit/<int:user_id>')
def edit_user(user_id):
    return 'edit user'


@dashboard.route('/profile')
def my_profile():
    return 'my profile'


# 外观
@dashboard.route('/appearance')
def appearance():
    return redirect(url_for('dashboard.navigations'))


@dashboard.route('/appearance/navigations')
def navigations():
    return 'navigations'


@dashboard.route('/appearance/footer-navigations')
def footer_navigations():
    return 'footer navigations'


# 设置
@dashboard.route('/settings')
def settings():
    return redirect(url_for('dashboard.general'))


@dashboard.route('/settings/general')
def general_setting():
    return render_template('dashboard/dash_setting_general.html', request=request)


@dashboard.route('/settings/writing')
def writing_setting():
    return 'writing settings'


@dashboard.route('/settings/reading')
def reading_setting():
    return 'reading settings'


@dashboard.route('/settings/discussion')
def discussion_setting():
    return 'discussion settings'
