# coding=utf-8

from flask import request
from flask import jsonify
from flask import g

from . import api
from ..api import auth

from app.core.models.posts import Post


@api.route('/posts', methods=['POST'])
@auth.login_required
def add_post():
    if not g.current_user.can('add_posts'):
        return jsonify({'success': 0, 'error': 'permission denied', 'message': u'没有权限添加文章'})
    pid_token = request.form.get('pidToken', '')
    if pid_token:
        post_id = Post.get_pid_from_token(pid_token)
    title = request.form.get('title', 'Untitled')
    markdown = request.form.get('markdown')
    html =  # markdown 转换 html,在模型中做
    slug = request.form.get('slug')
    return ''
