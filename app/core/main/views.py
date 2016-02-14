# coding=utf-8

from datetime import datetime
import json

from flask import current_app
from flask import send_file
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask.ext.login import current_user

from . import main
from app.core.models.helpers.redis_cache_decorator import redis_cached
from app.core.models.settings import Setting


@main.route('/favicon.ico')
def favicon():
    """
    收藏夹栏图标
    :return:
    """
    return send_file('static/dist/images/favicon.ico', as_attachment=False)


@main.route('/kill-ie.html')
def kill_ie():
    """
    kill ie
    :return:
    """
    return render_template('utils/kill-ie.html', blog_name=Setting.get_setting('blog_name', 'Plog'))


# 搜索
@main.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        s = request.form.get('s')
        return redirect('/search?s='+s)
    else:
        s = request.args.get('s')
    return s  # TODO search


# 首页
@main.route('/')
@redis_cached(timeout=30, key_prefix='aa')
def index():
    settings = Setting.get_setting('navigation')
    if settings:
        settings = (json.loads(settings)).get('navigations')
    return render_template('home.html', Setting=Setting, nav_settings=settings)






