# coding=utf-8

import re

from flask import request
from flask import redirect
from flask import url_for
from flask import flash
from flask import render_template
from flask import abort
from flask.ext.login import current_user

from . import dashboard
from .forms import EditTopNaviForm
from .forms import EditBottomNaviForm
from .forms import GeneralSettingForm
from .forms import ReadingSettingForm
from .forms import DiscussionSettingForm
from app.core.models.settings import Setting


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
    return render_template('error_pages/403.html'), 403


@dashboard.errorhandler(404)
def error_404(e):
    return render_template('error_pages/404.html'), 404


@dashboard.errorhandler(502)
def error_502(e):
    return render_template('error_pages/502.html'), 502


# 首页
@dashboard.route('/')
def dashboard_home():
    return redirect(url_for('dashboard.all_posts'))  # TODO more


# 文章
@dashboard.route('/post')
def posts():
    return redirect(url_for('dashboard.all_posts'))


@dashboard.route('/post/all')
def all_posts():
    return render_template('dashboard/dash_post_list.html', request=request)


@dashboard.route('/post/editor')
def new_post():
    return render_template('dashboard/dash_post_edit.html', request=request)


@dashboard.route('/post/editor/<int:post_id>')
def edit_post():
    return render_template('dashboard/dash_post_edit.html', request=request)


# 标签
@dashboard.route('/tags')
def tags():
    return redirect(url_for('dashboard.all_tags'))


@dashboard.route('/tags/all')
def all_tags():
    return render_template('dashboard/dash_tag_list.html', request=request)


# 用户
@dashboard.route('/users')
def users():
    return redirect(url_for('dashboard.all_users'))


@dashboard.route('/users/all')
def all_users():
    return render_template('dashboard/dash_user_list.html', request=request)


@dashboard.route('/users/new')
def new_user():
    return render_template('dashboard/dash_user_add.html', request=request)


@dashboard.route('/users/edit/<int:user_id>')
def edit_user(user_id):
    return render_template('dashboard/dash_user_edit.html', request=request)


@dashboard.route('/users/myprofile')
def my_profile():
    return render_template('dashboard/dash_user_me.html', request=request)


# 外观
@dashboard.route('/appearance')
def appearance():
    return redirect(url_for('dashboard.navigations'))


@dashboard.route('/appearance/navigations', methods=['GET', 'POST'])
def navigations():
    form = EditTopNaviForm()
    if form.validate_on_submit():
        navs = request.form.get('naviSettings')
        if navs and current_user.is_administrator:
            Setting.update_setting('navigation', navs)
        return redirect(url_for('dashboard.navigations'))
    return render_template('dashboard/dash_appearance_navigation.html', navi_form=form)


@dashboard.route('/appearance/footer-navigations', methods=['GET', 'POST'])
def footer_navigations():
    form = EditBottomNaviForm()
    if form.validate_on_submit():
        links = request.form.get('linkSettings')
        if links and current_user.is_administrator:
            Setting.update_setting('link', links)
        return redirect(url_for('dashboard.footer_navigations'))
    return render_template('dashboard/dash_appearance_footnavi.html', form=form)


# 设置
@dashboard.route('/settings')
def settings():
    return redirect(url_for('dashboard.general'))


@dashboard.route('/settings/general', methods=['GET', 'POST'])
def general_setting():
    form = GeneralSettingForm()
    if form.validate_on_submit():
        # print(request.form)
        if current_user.is_administrator:
            reg = re.compile('general\[([a-zA-Z0-9_]+)\]')
            for key, value in request.form.iteritems():
                options = reg.findall(key)
                if options:
                    Setting.update_setting(options[0], value)
        return redirect(url_for('dashboard.general_setting'))
    return render_template('dashboard/dash_setting_general.html', form=form)


@dashboard.route('/settings/writing')
def writing_setting():
    pass  # TODO
    return render_template('dashboard/dash_setting_writing.html', request=request)


@dashboard.route('/settings/reading', methods=['GET', 'POST'])
def reading_setting():
    form = ReadingSettingForm()
    if form.validate_on_submit():
        if current_user.is_administrator:
            reg = re.compile('reading\[([a-zA-Z0-9_]+)\]')
            for key, value in request.form.iteritems():
                options = reg.findall(key)
                if options:
                    Setting.update_setting(options[0], value)
        return redirect(url_for('dashboard.reading_setting'))
    return render_template('dashboard/dash_setting_reading.html', form=form)


@dashboard.route('/settings/discussion', methods=['GET', 'POST'])
def discussion_setting():
    form = DiscussionSettingForm()
    if form.validate_on_submit():
        if current_user.is_administrator:
            reg = re.compile('discussion\[([a-zA-Z0-9_]+)\]')
            for key, value in request.form.iteritems():
                options = reg.findall(key)
                if options:
                    Setting.update_setting(options[0], value)
        return redirect(url_for('dashboard.discussion_setting'))
    return render_template('dashboard/dash_setting_discussion.html', form=form)
