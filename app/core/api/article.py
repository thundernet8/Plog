# coding=utf-8

from flask import request
from flask import jsonify
from flask.ext.login import login_user

from . import api
from .errors import value_error
from .errors import action_failed
from app.core.models.users import User
from app.core.models.helpers.redis_cache_decorator import redis_cached


@api.route('/posts/<int:post_id>/comments', methods=['POST'])
@redis_cached(timeout=60, key_prefix='api/%s')
def article_comment(post_id):
    """
    操作文章评论
    :param post_id: 文章 id
    :return: 结果 json
    """
    return 'json-comment'  # TODO
