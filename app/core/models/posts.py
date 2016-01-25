# coding=utf-8

import time
from datetime import datetime

import flask_pymongo
from flask import abort
from flask.ext.login import current_user

from app import mongo
from .settings import Setting
from .mongo_counter import get_next_sequence
from .helpers.pagination import Pagination


class Post(object):
    """
    文章模型
    :post_id 文章 id
    :title 文章标题
    :slug 文章别名
    :markdown 文章内容,markdown格式
    :html 文章内容,html格式
    :image 文章特色图片
    :featured 是否推荐文章
    :type 文章类型,post/page,默认post
    :status 文章状态 trash/draft/pending/published
    :meta_title SEO 标题信息
    :meta_description SEO 描述信息
    :author_id 文章作者 id
    :create_at 文章创建时间戳
    :update_at 文章更新时间戳
    :update_by 更新文章作者 id
    :publish_at 文章发布时间戳
    :comment_status 文章评论状态
    :comment_count 文章评论数量
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
        mongo.db.settings.create_index([("post_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.settings.create_index([("slug", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.settings.create_index([("create_at", flask_pymongo.ASCENDING)])
        mongo.db.settings.create_index([("publish_at", flask_pymongo.ASCENDING)])
        mongo.db.settings.create_index([("comment_count", flask_pymongo.ASCENDING)])

    ##
    # 文章实例
    ##
    def __init__(self, **kwargs):
        """
        文章实例化
        :param kwargs: 文章字段键值对
        :return:
        """
        self.post_id = kwargs.get('post_id')
        self.title = kwargs.get('title', None)
        self.slug = kwargs.get('slug', None)
        self.markdown = kwargs.get('markdown', None)
        self.html = kwargs.get('html', None)
        self.image = kwargs.get('image', None)
        self.featured = kwargs.get('featured', None)
        self.type = kwargs.get('type', 'post')
        self.status = kwargs.get('status', None)
        self.meta_title = kwargs.get('meta_title', None)
        self.meta_description = kwargs.get('meta_description', None)
        self.author_id = kwargs.get('author_id', 0)
        self.create_at = datetime.fromtimestamp(int(kwargs.get('create_at', 0)))
        self.update_at = datetime.fromtimestamp(int(kwargs.get('update_at', 0)))
        self.update_by = kwargs.get('update_by', 0)
        self.publish_at = datetime.fromtimestamp(int(kwargs.get('publish_at', 0)))
        self.comment_status = kwargs.get('comment_status', 1)
        self.comment_count = kwargs.get('comment_count', 0)

    ##
    # 文章操作
    ##
    @staticmethod
    def get_post_by_field(field, value):
        """
        根据文章字段获取文章对象
        :param field: 文章字段(id/post_id/slug)
        :param value: 字段值
        :return: 文章对象 or None
        """
        if field == 'id':
            field = 'post_id'
        try:
            result = mongo.db.posts.find_one({field: value})
            if result:
                return Post(**result)
            else:
                return None
        except:
            return None

    @staticmethod
    def get_post(post_id):
        """
        根据文章 id 查询文章对象(alias get_post_by_id)
        :param post_id: 文章 id
        :return: 文章对象 or None
        """
        return Post.get_post_by_field('post_id', post_id)

    @staticmethod
    def get_post_by_id(post_id):
        """
        根据文章 id 查询文章对象
        :param post_id: 文章 id
        :return: 文章对象 or None
        """
        return Post.get_post_by_field('post_id', post_id)

    @staticmethod
    def get_post_by_slug(slug):
        """
        根据文章 slug 查询文章对象
        :param slug: 文章别名
        :return: 文章对象 or None
        """
        return Post.get_post_by_field('slug', slug)

    @staticmethod
    def draft_post(post_id, **kwargs):
        """
        保存文章草稿或创建新文章草稿
        :param post_id: 文章 id,新草稿为None
        :param kwargs: 文章字段键值对
        :return: 成功返回文章 id,失败返回 False
        """
        set = dict(kwargs)
        set.update({
            'status': 'draft',
            'update_at': int(time.time())
        })
        if not set.get('update_by'):
            set['update_by'] = str(current_user.get_id())
        if set.get('create_at'):
            del set['create_at']
        try:
            result = mongo.db.posts.update_one({
                'post_id': post_id
            }, {
                '$set': set,
                '$setOnInsert': {
                    'post_id': get_next_sequence('post_id'),
                    'create_at': int(time.time())
                }
            }, upsert=True)
            if result and result.modified_count > 0:
                return str(result.get('post_id'))
            return False
        except:
            return False

    @staticmethod
    def publish_post(post_id, **kwargs):
        """
        发表文章(任何文章发表前经由草稿阶段)
        :param post_id: 文章 id
        :return: 成功返回 文章 id,失败返回 False
        """
        set = dict(kwargs)
        set.update({
            'status': 'published',
            'update_at': int(time.time())
        })
        if not set.get('author_id'):
            set['author_id'] = str(current_user.get_id())
        if not set.get('update_by'):
            set['update_by'] = str(current_user.get_id())
        if not set.get('publish_at'):
            set['publish_at'] = int(time.time())
        if not set.get('comment_status'):
            set['comment_status'] = 1
        if set.get('create_at'):
            del set['create_at']
        try:
            result = mongo.db.posts.update_one({
                'post_id': post_id
            }, {
                '$set': set,
                '$setOnInsert': {
                    'post_id': get_next_sequence('post_id'),
                    'create_at': int(time.time())
                }
            })
            if result and result.modified_count > 0:
                return str(result.get('post_id'))
            return False
        except:
            return False

    @staticmethod
    def update_post(post_id, **kwargs):
        """
        更新文章
        :param post_id: 文章 id
        :param kwargs: 文章字段键值对
        :return: 成功返回文章 id,失败返回 False
        """
        set = dict(kwargs)
        set.update({
            'update_at': int(time.time())
        })
        if not set.get('update_by'):
            set['update_by'] = str(current_user.get_id())
        if set.get('create_at'):
            del set['create_at']
        try:
            result = mongo.db.posts.update_one({
                'post_id': post_id
            }, {
                '$set': set
            })
            if result and result.modified_count > 0:
                return str(result.get('post_id'))
            return False
        except:
            return False

    @staticmethod
    def trash_post(post_id):
        """
        废弃文章
        :param post_id: 文章 id
        :return: 删除成功返回 True,否则返回 False
        """
        try:
            result = mongo.db.posts.update_one({
                'post_id': post_id
            }, {
                'status': 'trash'
            })
            if result and result.modified_count > 0:
                return True
            return False
        except:
            return False

    @staticmethod
    def delete_post(post_id):
        """
        删除文章记录
        :param post_id: 文章 id
        :return:
        """
        try:
            result = mongo.db.posts.delete_one({
                'post_id': post_id
            })
            if result and result.deleted_count > 0:
                return True
            return False
        except:
            return False


    ##
    # 文章集合
    #
    @staticmethod
    def get_posts(filters, offset=0, limit=0, order_by='publish_at', order=flask_pymongo.DESCENDING):
        """
        查询文章集合
        :param filters: 过滤器
        :param offset: 偏移量
        :param limit: 最多返回的结果数量
        :param order_by: 排序依据
        :param order: 升/降序
        :return: 文章对象数组 or None
        """
        try:
            results = mongo.db.posts.find(filters, skip=offset, limit=limit).sort({order_by: order})
            if results:
                posts = []
                for result in results:
                    post = Post(**dict(result))
                    posts.append(post)
                return posts
            return None
        except:
            return None

    @staticmethod
    def get_paged_posts(posts_per_page, page=1, filters=None, order_by='publish_at', order=flask_pymongo.DESCENDING):
        """
        获取文章分页
        :param posts_per_page: 每页文章数
        :param page: 分页页码
        :param filters: 过滤器
        :param order_by: 排序依据
        :param order: 升/降序
        :return: 文章数组 or None
        """
        if page < 1:
            return None
        if not posts_per_page:
            posts_per_page = Setting.get_setting('posts_per_page', default=10)
        try:
            results = mongo.db.posts.find(filters, skip=posts_per_page*(page-1), limit=posts_per_page)\
                .sort({order_by: order})
            posts = []
            for result in results:
                post = Post(**dict(result))
                posts.append(post)
            return posts
        except:
            return None


class Posts(object):
    """
    文章对象数组模型,用于分页等集合查询
    """

    def __init__(self, **kwargs):
        """
        模型初始化,引入参数
        :param kwargs: 文章集合查询参数
        :return:
        """
        self.filters = kwargs.get('filters', dict())
        self.filters['type'] = 'post'
        self.order_by = kwargs.get('order_by', 'publish_at')
        self.order = kwargs.get('order', flask_pymongo.DESCENDING)

    def pagination(self, posts_per_page, page=1, error_out=True):
        """
        获取文章分页模型
        :param posts_per_page: 每页文章数
        :param page: 分页页码
        :param error_out: 是否显示错误信息
        :return: Pagination 对象 or None
        """
        if page < 1 and error_out:
            abort(404)
        if not posts_per_page:
            posts_per_page = Setting.get_setting('posts_per_page', default=10)
        try:
            results = mongo.db.posts.find(self.filters, skip=posts_per_page*(page-1), limit=posts_per_page)\
                .sort({self.order_by: self.order})
            count = results.count
            if (not results or count == 0) and page != 1 and error_out:
                abort(404)
        except:
            if error_out and page != 1:
                abort(404)
            return None
        if page == 1 and count < posts_per_page:
            total = count
        else:
            total = mongo.db.posts.count(self.filters)
        posts = []
        for result in results:
            post = Post(**dict(result))
            posts.append(post)

        return Pagination(self, posts_per_page, page, total, posts)
