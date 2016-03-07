# coding=utf-8

from datetime import datetime
import json

from flask import current_app
from flask import send_file
from flask import request
from flask import render_template
from flask import session
from flask import redirect
from flask import abort
from flask.ext.login import current_user

from . import main
from app.core.models.helpers.redis_cache_decorator import redis_cached
from app.core.models.settings import Setting
from app.core.models.posts import Post
from app.core.models.posts import Posts
from app.core.models.users import User
from .forms import CommentForm


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
    pagenation = Posts(filters={'status': 'published'}).pagination()
    posts = pagenation.items if pagenation else []
    return render_template('home.html', posts=posts, pagenation=pagenation)


# 首页(带分页)
@main.route('/page/<int:page>')
@redis_cached(timeout=30, key_prefix='home_html_%s')
def index_paged(page):
    pagenation = Posts(filters={'status': 'published'}).pagination(page=page)
    posts = pagenation.items if pagenation else []
    return render_template('home.html', posts=posts, pagenation=pagenation)


# 文章详情页
@main.route('/article/<int:post_id>.html')
@redis_cached(timeout=30, key_prefix='article_%s')
def article_detail(post_id):
    post = Post.get_post(post_id)
    if not post or not post.post_id or post.status != 'published':
        abort(404)
    author = User(user_id=post.author_id)
    comment_form = CommentForm()
    return render_template('article.html', post=post, author=author, comment_form=comment_form)


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


# TAG
@main.route('/tag/<int:tag_id>')
@redis_cached(timeout=600, key_prefix='tag_%s')
def tag(tag_id):
    return 'tag page' + str(tag_id)  # TODO tag


# 404
@main.errorhandler(404)
def main_404(e):
    return render_template('error_pages/404.html'), 404





