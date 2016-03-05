# coding=utf-8

from flask import request
from flask import jsonify
from flask import g

from . import api
from ..api import auth

from app.core.models.tags import Tag


@api.route('/tags/<string:tag_name>', methods=['PUT'])
@auth.login_required
def add_tag(tag_name):
    if not (g.current_user.can('add_tags')):
        return jsonify({'success': 0, 'error': 'permission denied', 'message': u'没有权限添加标签'})
    tag_id = Tag.add_tag(tag_name)
    tag_id = tag_id or 0
    return jsonify({'success': 1, 'tagName': tag_name, 'tagId': tag_id})
