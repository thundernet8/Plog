# coding=utf-8

import time
from datetime import datetime

from flask import abort
from flask import request
from flask.ext.login import current_user
import flask_pymongo

from app import mongo
import posts
from .mongo_counter import get_next_sequence
from .settings import Setting
from .helpers.pagination import Pagination
from .helpers.redis_cache_decorator import redis_memoize


class Comment(object):
    """
    评论模型
    :comment_id 评论 id
    :post_id 评论所在文章 id
    :user_id 评论作者 id
    :ip 评论者 IP
    :agent 评论者 UA 信息
    :create_at 评论时间戳
    :content 评论内容
    :approved 评论是否通过
    :parent 评论父级评论 id
    :mail_notify 评论被回复是否邮件提醒
    """

    ##
    # 数据库部署
    ##
    @staticmethod
    def create_table_indexes():
        """
        创建数据库若干字段唯一索引,程序部署初始化调用
        :return:
        """
        mongo.db.permissions_roles.create_index([("comment_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.permissions_roles.create_index([("post_id", flask_pymongo.ASCENDING)])
        mongo.db.permissions_roles.create_index([("user_id", flask_pymongo.ASCENDING)])
        mongo.db.permissions_roles.create_index([("create_at", flask_pymongo.ASCENDING)])
        mongo.db.permissions_roles.create_index([("parent", flask_pymongo.ASCENDING)])

    ##
    # 评论实例
    ##
    def __init__(self, **kwargs):
        """
        评论实例化
        :param kwargs: 评论字段键值对
        :return:
        """
        self.comment_id = kwargs.get('comment_id')
        self.post_id = kwargs.get('post_id')
        self.user_id = kwargs.get('user_id')
        self.ip = kwargs.get('ip', '')
        self.agent = kwargs.get('agent', '')
        self.create_at = datetime.fromtimestamp(int(kwargs.get('create_at', 0)))
        self.content = kwargs.get('content')
        self.approved = kwargs.get('approved', 0)
        self.parent = kwargs.get('parent', 0)
        self.mail_notify = kwargs.get('mail_notify', 1)

    ##
    # 评论操作
    ##
    @staticmethod
    def get_comment_by_id(comment_id):
        """
        根据评论 id 获取文章对象
        :param comment_id: 评论 id
        :return: 评论对象 or None
        """
        try:
            result = mongo.db.comments.find_one({'comment_id': comment_id})
            if result:
                return Comment(**dict(result))
            else:
                return None
        except:
            return None

    @staticmethod
    def get_comment(comment_id):
        """
        根据评论 id 获取文章对象(alias)
        :param comment_id: 评论 id
        :return: 评论对象 or None
        """
        return Comment.get_comment_by_id(comment_id)

    @staticmethod
    def approve_comment(comment_id):
        """
        审核通过评论
        :param comment_id: 评论 id
        :return: 成功返回 True,否则False
        """
        try:
            result = mongo.db.comments.update_one({
                'comment_id': comment_id
            }, {
                'approved': 1
            })
            if result and result.modified_count > 0:
                comment = Comment.get_comment(comment_id)
                posts.Post.update_post_comment_count(comment.comment_id)
                return True
            return False
        except:
            return False

    @staticmethod
    def trash_comment(comment_id):
        """
        标记垃圾评论
        :param comment_id: 评论 id
        :return: 删除成功返回 True,否则False
        """
        try:
            result = mongo.db.comments.update_one({
                'comment_id': comment_id
            }, {
                'approved': 0
            })
            if result and result.modified_count > 0:
                comment = Comment.get_comment(comment_id)
                posts.Post.update_post_comment_count(comment.comment_id)
                return True
            return False
        except:
            return False

    @staticmethod
    def add_comment(**kwargs):
        """
        发表评论
        :param kwargs: 评论字段键值对
        :return: 成功返回评论 id,失败返回 False
        """
        if not current_user.is_logged_in:  # 禁止匿名用户评论
            return False
        sets = dict(kwargs)
        sets['user_id'] = current_user.user_id
        sets['create_at'] = int(time.time())
        sets['approved'] = 1
        sets['mail_notify'] = 1
        sets['comment_id'] = get_next_sequence('comment_id')
        if not sets.get('ua'):
            sets['ua'] = request.user_agent.string
        if not sets.get('ip'):
            sets['ip'] = request.remote_addr
        try:
            result = mongo.db.comments.insert_one(sets)
            if result and result.inserted_id:
                if sets.get('post_id'):
                    posts.Post.update_post_comment_count(sets.get('post_id'))
                return sets['comment_id']
            return False
        except:
            return False

    @staticmethod
    def update_comment(comment_id, **kwargs):
        """
        更新评论
        :param comment_id: 评论 id
        :param kwargs:  待更新评论字段键值对
        :return: 更新成功返回 True,否则 False
        """
        sets = dict(kwargs)
        if sets.get('create_at'):
            del sets['create_at']
        try:
            result = mongo.db.comments.update_one({
                'comment_id': comment_id
            }, {
                '$set': sets
            })
            if result and result.modified_count > 0:
                comment = Comment.get_comment(comment_id)
                posts.Post.update_post_comment_count(comment.comment_id)
                return True
            return False
        except:
            return False

    @staticmethod
    def delete_comment(comment_id):
        """
        删除评论记录
        :param comment_id: 评论 id
        :return: 删除成功返回 True,否则False
        """
        try:
            result = mongo.db.comments.delete_one({
                'comment_id': comment_id
            })
            if result and result.deleted_count > 0:
                comment = Comment.get_comment(comment_id)
                posts.Post.update_post_comment_count(comment.comment_id)
                return True
            return False
        except:
            return False

    ##
    # 评论集合
    ##
    @staticmethod
    def get_comments(filters, offset=0, limit=20, order_by='create_at', order=flask_pymongo.DESCENDING):
        """
        获取评论
        :param filters: 过滤器 //post_id/user_id/parent/approved
        :param offset: 偏移量
        :param limit: 最多返回的结果数量
        :param order_by: 排序依据
        :param order: 升/降序
        :return: 评论对象列表 or None
        """
        try:
            results = mongo.db.comments.find(filters, skip=offset,
                                             limit=limit).sort({order_by: order})
            if results:
                comments = []
                for result in results:
                    comment = Comment(**dict(result))
                    comments.append(comment)
                return comments
            return None
        except:
            return None

    @staticmethod
    @redis_memoize(timeout=60)
    def get_comments_count(filters):
        """
        获取评论数量
        :param filters: 过滤器
        :return: 评论数量
        """
        if not isinstance(filters, dict):
            return 0
        if not filters.get('approved'):
            filters['approved'] = 1  # 默认只选择已审核评论
        try:
            count = mongo.db.comments.count(filters)
            return count
        except:
            return 0

    @staticmethod
    def get_post_comments(post_id, approved=True, offset=0, limit=20, order_by='create_at', order=flask_pymongo.DESCENDING):
        """
        获取文章评论
        :param post_id: 文章 id
        :param approved: 评论状态
        :param offset: 偏移量
        :param limit: 最多返回的结果数量
        :param order_by: 排序依据
        :param order: 升/降序
        :return: 评论对象列表 or None
        """
        try:
            results = mongo.db.comments.find({'post_id': post_id, 'approved': int(approved)}, skip=offset,
                                             limit=limit).sort({order_by: order})
            if results:
                comments = []
                for result in results:
                    comment = Comment(**dict(result))
                    comments.append(comment)
                return comments
            return None
        except:
            return None

    @staticmethod
    def get_paged_comments(comments_per_page, page=1, filters=None, order_by='publish_at', order=flask_pymongo.DESCENDING):
        """
        获取文章评论
        :param comments_per_page: 每页显示的评论数量
        :param page: 页码
        :param filters: 过滤器(字典对象)
        :param order_by: 排序依据
        :param order: 升/降序
        :return: 评论对象列表 or None
        """
        if page < 1:
            return None
        if not comments_per_page:
            comments_per_page = Setting.get_setting('comments_per_page', default=20)
        try:
            results = mongo.db.comments.find(filters, skip=comments_per_page*(page-1), limit=comments_per_page)\
                .sort({order_by: order})
            comments = []
            for result in results:
                comment = Comment(**dict(result))
                comments.append(comment)
            return comments
        except:
            return None


class Comments(object):
    """
    评论对象列表模型,用于分页等集合查询
    """

    def __init__(self, **kwargs):
        """
        模型初始化,引入参数
        :param kwargs: 评论集合查询参数
        :return:
        """
        self.filters = kwargs.get('filters', dict())
        self.order_by = kwargs.get('order_by', 'create_at')
        self.order = kwargs.get('order', flask_pymongo.DESCENDING)

    def pagination(self, comments_per_page, page=1, error_out=True):
        """
        获取文章分页模型
        :param comments_per_page: 每页评论数
        :param page: 分页页码
        :param error_out: 是否显示错误信息
        :return: Pagination 对象 or None
        """
        if page < 1 and error_out:
            abort(404)
        if not comments_per_page:
            comments_per_page = int(Setting.get_setting('comments_per_page', default=20))
        try:
            results = mongo.db.comments.find(self.filters, skip=comments_per_page*(page-1), limit=comments_per_page)\
                .sort({self.order_by: self.order})
            count = results.count
            if (not results or count == 0) and page != 1 and error_out:
                abort(404)
        except:
            if error_out and page != 1:
                abort(404)
            return None
        if page == 1 and count < comments_per_page:
            total = count
        else:
            total = mongo.db.comments.count(self.filters)
        comments = []
        for result in results:
            comment = Comment(**dict(result))
            comments.append(comment)

        return Pagination(self, comments_per_page, page, total, comments)
