# coding=utf-8

import flask_pymongo

from app import mongo

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
        mongo.db.settings.create_index([("comment_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.settings.create_index([("post_id", flask_pymongo.ASCENDING)])
        mongo.db.settings.create_index([("user_id", flask_pymongo.ASCENDING)])
        mongo.db.settings.create_index([("create_at", flask_pymongo.ASCENDING)])
        mongo.db.settings.create_index([("parent", flask_pymongo.ASCENDING)])

    ##
    # 评论实例
    ##
    def __init__(self, **kwargs):
        """
        评论实例化
        :param kwargs: 评论字段键值对
        :return:
        """

