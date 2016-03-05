# coding=utf-8

from datetime import datetime

import flask_pymongo

from app import mongo
from pymongo.errors import DuplicateKeyError
from .mongo_counter import get_next_sequence
from .helpers.slug_generator import get_slug


class Tag(object):
    """
    文章标签模型(可做分类)
    :tag_id 标签 id
    :name 标签名
    :slug 标签别名
    :description 标签描述
    :image 标签图像
    :hidden 是否隐藏标签,默认不隐藏,即0
    :parent_id 父级 id
    :meta_title SEO 标题信息
    :meta_description SEO 描述信息
    :create_at 创建时间
    :create_by 创建者 id
    :update_at 更新时间
    :update_by 更新者 id
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
        mongo.db.tags.create_index([("tag_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.tags.create_index([("name", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.tags.create_index([("slug", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.tags.create_index([("create_at", flask_pymongo.ASCENDING)])
        mongo.db.tags.create_index([("update_at", flask_pymongo.ASCENDING)])

    ##
    # 标签实例
    ##
    def __init__(self, **kwargs):
        """
        标签实例化
        :param kwargs: 标签字段键值对
        :return:
        """
        self.tag_id = kwargs.get('tag_id', None)
        self.name = kwargs.get('name', None)
        self.slug = kwargs.get('slug', None)
        self.description = kwargs.get('description')
        self.image = kwargs.get('image')
        self.hidden = kwargs.get('hidden', 0)
        self.parent_id = kwargs.get('parent_id', 0)
        self.meta_title = kwargs.get('meta_title')
        self.meta_description = kwargs.get('meta_description')
        self.create_at = datetime.fromtimestamp(int(kwargs.get('create_at', 0)))
        self.create_by = kwargs.get('create_by', 0)
        self.update_at = datetime.fromtimestamp(int(kwargs.get('update_at', 0)))
        self.update_by = kwargs.get('update_by', 0)

    ##
    # 标签查询
    ##
    @staticmethod
    def get_tag_by_field(field, value):
        """
        根据文章字段获取标签对象
        :param field: 标签字段(id/tag_id/name/slug)
        :param value: 字段值
        :return: 标签对象 or None
        """
        if field == 'id':
            field = 'tag_id'
        try:
            result = mongo.db.tags.find_one({field: value})
            if result:
                tag = Tag(**dict(result))
                return tag
            return None
        except:
            return None

    @staticmethod
    def get_tag_by_id(tag_id):
        """
        根据标签 id 查询标签
        :param tag_id: 标签 id
        :return: 标签对象 or None
        """
        return Tag.get_tag_by_field('tag_id', tag_id)

    @staticmethod
    def get_tag_by_name(name):
        """
        根据标签名查询标签
        :param name: 标签名
        :return: 标签对象 or None
        """
        return Tag.get_tag_by_field('name', name)

    @staticmethod
    def get_tag_by_slug(slug):
        """
        根据标签别名查询标签
        :param slug: 标签别名
        :return: 标签对象 or None
        """
        return Tag.get_tag_by_field('slug', slug)

    ##
    # 标签操作(更新/添加)
    ##
    @staticmethod
    def update_tag(tag_id, **kwargs):
        """
        更新标签
        :param tag_id: 标签 id
        :param kwargs: 标签字段键值对
        :return: 成功返回 True,否则返回 False
        """
        try:
            result = mongo.db.tags.update_one({
                'tag_id': tag_id
            }, {'$set': kwargs}, upsert=False)
            if result and result.modified_count > 0:
                return True
            return False
        except:
            return False

    @staticmethod
    def add_tag(name):
        """
        添加标签
        :param name: 标签名
        :return: 增加/更新的标签 id or None
        """
        slug = get_slug(name)
        slug_count = 0
        try:
            count = mongo.db.tags.count({'slug': slug})
            slug_count = count
        except:
            pass
        if slug_count:
            slug = '-'.join([slug, str(slug_count+1)])
        try:
            result = mongo.db.tags.update_one({
                'name': name
            }, {
                '$setOnInsert': {
                    'tag_id': get_next_sequence('tag_id'),
                    'slug': slug
                }
            }, upsert=True)
            tag = mongo.db.tags.find_one({'name': name})
            if result and tag:
                return tag.get('tag_id')
        except:
            return None
