# coding=utf-8

import flask_pymongo

from app import mongo


class Role(object):
    """
    用户角色
    """

    def __init__(self):
        pass

    @staticmethod
    def insert_default_roles():
        roles = [
            {
                'rid': 1,
                'name': 'Administrator',
                'description': u'管理员',
            },
            {
                'rid': 2,
                'name': 'Editor',
                'description': u'编辑',
            },
            {
                'rid': 3,
                'name': 'Author',
                'description': u'作者',
            },
            {
                'rid': 4,
                'name': 'Owner',
                'description': u'博客所有者',
            }
        ]

        # 创建唯一索引键
        mongo.db.roles.create_index([("rid", flask_pymongo.ASCENDING), ("name", flask_pymongo.ASCENDING)], unique=True)

        try:
            mongo.db.roles.insert(roles)
        except Exception:
            pass
