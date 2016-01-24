# coding=utf-8

import time
from datetime import datetime
from bson.objectid import ObjectId
import pymongo

import flask_pymongo
from flask import abort
from flask.ext.login import current_user

from app import mongo
from .settings import Setting
from .helpers.pagination import Pagination


class Tag(object):
    """
    文章标签模型
    :tag_id 标签 id
    :name 标签名
    :slug 标签别名
    :description 标签描述
    :image 标签图像
    :hidden 是否隐藏标签,默认不隐藏,即0
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
        mongo.db.settings.create_index([("tag_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.settings.create_index([("create_at", flask_pymongo.ASCENDING)])
        mongo.db.settings.create_index([("update_at", flask_pymongo.ASCENDING)])

    ##
    # 文章实例
    ##
    def __init__(self, **kwargs):
        """
        标签实例化
        :param kwargs: 标签字段键值对
        :return:
        """
        self.tag_id = kwargs.get('tag_id')