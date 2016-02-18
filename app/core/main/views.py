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
from app.core.models.posts import Posts


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
@redis_cached(timeout=30, key_prefix='home_html')  # TODO 缓存时间
def index():
    settings = Setting.get_setting('navigation')
    if settings:
        settings = (json.loads(settings)).get('navigations')
    pagenation = Posts(filters={'status': 'published'}).pagination()
    posts = pagenation.items if pagenation else []
    return render_template('home.html', nav_settings=settings, posts=posts, pagenation=pagenation)


# 首页(带分页)
@main.route('/page/<int:page>')
@redis_cached(timeout=300, key_prefix='home_html_%s')
def index_paged(page):
    settings = Setting.get_setting('navigation')
    if settings:
        settings = (json.loads(settings)).get('navigations')
    pagenation = Posts(filters={'status': 'published'}).pagination(page=page, posts_per_page=2)
    posts = pagenation.items if pagenation else []
    return render_template('home.html', nav_settings=settings, posts=posts, pagenation=pagenation)


# 文章详情页
@main.route('/article/<int:post_id>.html')
@redis_cached(timeout=300, key_prefix='article_%s')
def article_detail(post_id):
    return 'post detail'+str(post_id)  # TODO


# 用户/作者主页
@main.route('/author/<int:user_id>')
@redis_cached(timeout=300, key_prefix='author_%s')
def user_homepage(user_id):
    return 'user homepage'+str(user_id)  # TODO /考虑使用用户名或昵称替代用户 id 作为链接标识


# RSS
@main.route('/rss')
@redis_cached(timeout=600, key_prefix='rss')
def rss():
    return 'rss'  # TODO rss





