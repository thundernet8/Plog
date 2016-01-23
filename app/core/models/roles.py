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
        """
        插入默认角色并建立数据库索引,网站部署初始化使用
        :return:
        """
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

    @staticmethod
    def get_role_id(role):
        """
        根据角色查询角色 id
        :param role: 用户角色 Owner/Administrator/Editor/Author
        :return: 角色 id or None
        """
        roles = ['Owner', 'Administrator', 'Editor', 'Author']
        try:
            roles.index(role)
            return mongo.db.roles.find_one({'name': role}).get('rid', None)
        except:
            return None

    @staticmethod
    def get_role_name(role_id):
        """
        根据角色 id 查询角色
        :param role_id: 用户角色 id 1/2/3/4
        :return: 角色 or None
        """
        try:
            result = mongo.db.roles.find_one({'rid': role_id})
            return result.get('name', None)
        except:
            return None
