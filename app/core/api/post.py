# coding=utf-8

from flask import request
from flask import jsonify
from flask import g
from flask import url_for

from . import api
from ..api import auth
from .errors import action_failed
from app.core.models.posts import Post


@api.route('/posts', methods=['POST'])
@auth.login_required
def add_post():
    if not g.current_user.can('add_posts'):
        return jsonify({'success': 0, 'error': 'permission denied', 'message': u'没有权限添加文章'})
    pid_token = request.form.get('pidToken', '')
    if pid_token:
        post_id = Post.get_pid_from_token(pid_token)
    else:
        post_id = None
    title = request.form.get('title', 'Untitled')
    markdown = request.form.get('markdown')
    slug = request.form.get('slug')
    image = request.form.get('thumbUrl', '')
    meta_title = request.form.get('metaTitle', '')
    meta_description = request.form.get('metaDescription', '')
    type = 'page' if request.form.get('postType') == 'page' else 'post'
    tag_ids = request.form.get('tags', '')  # 为 tag id 以逗号拼接的字符串
    action = 'draft' if request.form.get('action') not in ['publish', 'update', 'draft'] else request.form.get('action')
    author_id = g.current_user.get_id()
    update_by = g.current_user.get_id()

    if post_id and action == 'update':
        pid = Post.update_post(post_id, title=title, markdown=markdown, slug=slug, image=image, meta_title=meta_title,
                               meta_description=meta_description, type=type, tag_ids=tag_ids,
                               author_id=author_id, update_by=update_by)
        if not pid:
            return action_failed(message=u'更新文章失败')
        post = Post.get_post_json(pid)
        return jsonify({'success': 1, 'post': post, 'postId': pid})

    if action == 'publish':
        pid = Post.publish_post(post_id, title=title, markdown=markdown, slug=slug, image=image, meta_title=meta_title,
                                meta_description=meta_description, type=type, tag_ids=tag_ids,
                                author_id=author_id, update_by=update_by)
        message = u'发表文章失败'
    else:
        pid = Post.draft_post(post_id, title=title, markdown=markdown, slug=slug, image=image, meta_title=meta_title,
                              meta_description=meta_description, type=type, tag_ids=tag_ids,
                              author_id=author_id, update_by=update_by)
        message = u'添加文章失败'
    if not pid:
        return action_failed(message=message)
    post = Post.get_post_json(pid)
    return jsonify({'success': 1, 'post': post, 'postId': pid, 'editUrl': url_for('dashboard.edit_post', post_id=pid,
                                                                                  _external=True)})
