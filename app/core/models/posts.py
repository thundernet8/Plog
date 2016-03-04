# coding=utf-8

import time
from datetime import datetime
from random import randint

import flask_pymongo
from flask import current_app
from flask import abort
from flask import url_for
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask.ext.login import current_user

from app import mongo
from .settings import Setting
#from .comments import Comment
import comments
from .mongo_counter import get_next_sequence
from .helpers.pagination import Pagination
from .helpers.slug_generator import get_slug
from .helpers.excerpt_generator import get_excerpt
from .helpers.redis_cache_decorator import redis_memoize


class Post(object):
    """
    文章模型
    :post_id 文章 id
    :title 文章标题
    :slug 文章别名
    :markdown 文章内容,markdown格式
    :html 文章内容,html格式
    :excerpt 文章摘要
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
    :view_count 阅读数量
    :tag_ids 文章标签 id 拼合字符串
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
        mongo.db.posts.create_index([("post_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.posts.create_index([("slug", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.posts.create_index([("create_at", flask_pymongo.ASCENDING)])
        mongo.db.posts.create_index([("publish_at", flask_pymongo.ASCENDING)])
        mongo.db.posts.create_index([("comment_count", flask_pymongo.ASCENDING)])
        mongo.db.posts.create_index([("view_count", flask_pymongo.ASCENDING)])

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
        self.excerpt = kwargs.get('excerpt', get_excerpt(self.html,
                                                         count=Setting.get_setting('excerpt_length', 120), wrapper=u''))
        self.image = kwargs.get('image', None)
        self.featured = kwargs.get('featured', False)
        self.type = kwargs.get('type', 'post')
        self.status = kwargs.get('status', None)  # trash/draft/pending/published
        self.meta_title = kwargs.get('meta_title', None)
        self.meta_description = kwargs.get('meta_description', None)
        self.author_id = kwargs.get('author_id', 0)
        self.create_at = datetime.fromtimestamp(int(kwargs.get('create_at', 0)))
        self.update_at = datetime.fromtimestamp(int(kwargs.get('update_at', 0)))
        self.update_by = kwargs.get('update_by', 0)
        self.publish_at = datetime.fromtimestamp(int(kwargs.get('publish_at', 0)))
        self.comment_status = kwargs.get('comment_status', 1)
        self.comment_count = kwargs.get('comment_count', 0)
        self.view_count = kwargs.get('view_count', 0)
        self.tag_ids = kwargs.get('tag_ids', '')

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
                return Post(**dict(result))
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
    def draft_post(post_id=None, **kwargs):
        """
        保存文章草稿或创建新文章草稿
        :param post_id: 文章 id,新草稿为None
        :param kwargs: 文章字段键值对
        :return: 成功返回文章 id,失败返回 False
        """
        sets = dict(kwargs)
        if not sets.get('type'):
            sets['type'] = 'post'
        if not sets.get('slug'):
            sets['slug'] = get_slug(sets.get('title'))
        sets['excerpt'] = get_excerpt(sets.get('html', u''),
                                      count=Setting.get_setting('excerpt_length', 120), wrapper=u'')
        slug_count = mongo.db.posts.count({'slug': sets.get('slug')})
        if slug_count > 0:
            new_slug = '-'.join([sets.get('slug'), str(slug_count+1)])
            while mongo.db.posts.count({'slug': new_slug}):
                slug_count += 1
                new_slug = '-'.join([sets.get('slug'), str(slug_count+1)])
            sets['slug'] = new_slug
        sets.update({
            'status': 'draft',
            'update_at': int(time.time())
        })
        if not sets.get('update_by'):
            sets['update_by'] = str(current_user.get_id())
        if sets.get('create_at'):
            del sets['create_at']
        try:
            result = mongo.db.posts.update_one({
                'post_id': post_id
            }, {
                '$set': sets,
                '$setOnInsert': {
                    'post_id': get_next_sequence('post_id'),
                    'create_at': int(time.time())
                }
            }, upsert=True)
            if result and result.modified_count > 0:
                return post_id
            if result and result.upserted_id:
                return mongo.db.posts.find_one({'_id': result.upserted_id}).get('post_id')
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
        sets = dict(kwargs)
        sets.update({
            'status': 'published',
            'update_at': int(time.time())
        })
        if not sets.get('type'):
            sets['type'] = 'post'
        if not sets.get('author_id'):
            sets['author_id'] = str(current_user.get_id())
        if not sets.get('update_by'):
            sets['update_by'] = str(current_user.get_id())
        if not sets.get('publish_at'):
            sets['publish_at'] = int(time.time())
        if not sets.get('comment_status'):
            sets['comment_status'] = 1
        if sets.get('create_at'):
            del sets['create_at']
        try:
            result = mongo.db.posts.update_one({
                'post_id': post_id
            }, {
                '$set': sets,
                '$setOnInsert': {
                    'post_id': get_next_sequence('post_id'),
                    'create_at': int(time.time())
                }
            }, upsert=True)
            if result and result.modified_count > 0:
                return post_id
            if result and result.upserted_id:
                return mongo.db.posts.find_one({'_id': result.upserted_id}).get('post_id')
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
        if not current_user.is_logged_in:
            return False
        sets = dict(kwargs)
        sets.update({
            'update_at': int(time.time())
        })
        if not sets.get('update_by'):
            sets['update_by'] = str(current_user.get_id())
        if sets.get('create_at'):
            del sets['create_at']
        try:
            result = mongo.db.posts.update_one({
                'post_id': post_id
            }, {
                '$set': sets
            })
            if result and result.modified_count > 0:
                return post_id
            return False
        except:
            return False

    @staticmethod
    def update_post_comment_count(post_id):
        """
        更新文章评论数量
        :param post_id: 文章 id
        :return: 更新成功返回文章 id,失败返回 False
        """
        count = Post.get_post_comment_count(post_id, approved=1)
        return Post.update_post(post_id, comment_count=count)

    @staticmethod
    @redis_memoize(timeout=60)
    def get_post_comment_count(post_id, approved=1):
        """
        获取文章评论数
        :param post_id: 文章 id
        :param approved: 评论审核状态, 0表示统计未通过评论,1表示统计已审核评论,all表示统计所有评论
        :return: 文章的评论数
        """
        filters = dict(post_id=post_id)
        if approved == 0 or approved == 1:
            filters['approved'] = approved
        try:
            count = mongo.db.comments.count(filters)
            return count
        except:
            return 0

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
        :return: 删除成功返回 True,否则False
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
    def get_posts(filters, offset=0, limit=10, order_by='publish_at', order=flask_pymongo.DESCENDING):
        """
        查询文章集合
        :param filters: 过滤器
        :param offset: 偏移量
        :param limit: 最多返回的结果数量
        :param order_by: 排序依据
        :param order: 升/降序
        :return: 文章对象列表 or None
        """
        filters['type'] = 'post'
        try:
            results = mongo.db.posts.find(filters, skip=offset, limit=limit).sort([(order_by, order)])
            if results:
                posts = []
                for result in results:
                    post = Post(**dict(result))
                    posts.append(post)
                return posts
            return None
        except Exception, e:
            print(e)
            return None

    @staticmethod
    def get_top_viewed_posts(limit=5):
        """
        获取热门文章(基于浏览数排序)
        :param limit: 最多返回的文章数量
        :return: 文章对象列表
        """
        posts = Post.get_posts(dict(status='published'), limit=limit, order_by='view_count')
        return posts

    @staticmethod
    def get_top_discussed_posts(limit=5):
        """
        获取热门文章(基于评论数排序)
        :param limit: 最多返回的文章数量
        :return: 文章对象列表
        """
        posts = Post.get_posts(dict(status='published'), limit=limit, order_by='comment_count')
        return posts

    @staticmethod
    @redis_memoize(timeout=60)
    def get_posts_count(filters):
        """
        统计文章数量
        :param filters: 过滤器
        :return: 文章数量
        """
        try:
            count = mongo.db.posts.count(filters)
            return count
        except:
            return 0

    @staticmethod
    def get_paged_posts(posts_per_page, page=1, filters=None, order_by='publish_at', order=flask_pymongo.DESCENDING):
        """
        获取文章分页
        :param posts_per_page: 每页文章数
        :param page: 分页页码
        :param filters: 过滤器(字典对象)
        :param order_by: 排序依据
        :param order: 升/降序
        :return: 文章数组 or None
        """
        filters['type'] = 'post'
        if page < 1:
            return None
        if not posts_per_page:
            posts_per_page = Setting.get_setting('posts_per_page', default=10)
        try:
            results = mongo.db.posts.find(filters, skip=posts_per_page*(page-1), limit=posts_per_page)\
                .sort([(order_by, order)])
            posts = []
            for result in results:
                post = Post(**dict(result))
                posts.append(post)
            return posts
        except:
            return None

    ##
    # 辅助
    #
    @staticmethod
    def get_random_thumb(start=1, end=40):
        """
        获取随机缩略图
        :param start: 起始图像 id
        :param end: 结束图像 id
        :return: 图像链接
        """
        id = randint(start, end)
        return url_for('static', filename='dist/images/thumbs/'+str(id)+'.jpg')

    def get_thumb(self, use_rand=True):
        """
        获取文章的特色图
        :param use_rand: 当无特色图时,是否采用随机缩略图
        :return: 缩略图或None
        """
        if not self.image and not use_rand:
            return None
        return self.image or Post.get_random_thumb()

    def get_permalink(self, external=False):
        """
        获取文章的固定链接
        :param external 是否显示完整链接
        :return: 文章固定链接
        """
        return url_for('main.article_detail', post_id=self.post_id, _external=external)

    def get_pid_token(self, expiration=3600*24):
        """
        加密文章 post_id 防止篡改
        :param expiration: token 过期时间
        :return: token 字符串
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'editor_pid': self.post_id}).decode('ascii')

    @staticmethod
    def get_pid_from_token(token):
        """
        从加密的 pid token 中获得原始 post_id
        :param token:  包含 post_id 信息的 token
        :return:  原始 post_id 或 0
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return 0
        return data.get('editor_pid', 0)


class Posts(object):
    """
    文章对象列表模型,用于分页等集合查询
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

    def pagination(self, posts_per_page=0, page=1, error_out=True):
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
            posts_per_page = int(Setting.get_setting('posts_per_page', default=10))
        try:
            results = mongo.db.posts.find(filter=self.filters, skip=posts_per_page*(page-1), limit=posts_per_page)\
                .sort([(self.order_by, self.order)])
            count = results.count()
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
