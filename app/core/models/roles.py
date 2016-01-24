# coding=utf-8

import flask_pymongo

from app import mongo
from .permissions_roles import PermissionsRoles


class Role(object):
    """
    用户角色
    :role_id 角色 id
    :name 角色名称
    :description 角色描述
    """

    def __init__(self, **kwargs):
        """
        实例化角色模型
        :param kwargs: 角色模型字段键值对
        :return: 角色实例
        """
        result = mongo.db.roles.find_one(kwargs)
        if result and result.count():
            self.role_id = result.get('role_id', 5)
            self.name = result.get('name', 'Reader')
            self.description = result.get('description', u'读者')

    @staticmethod
    def insert_default_roles():
        """
        插入默认角色并建立数据库索引,网站部署初始化使用
        :return:
        """
        roles = [
            {
                'role_id': 1,
                'name': 'Owner',
                'description': u'博客所有者'
            },
            {
                'role_id': 2,
                'name': 'Administrator',
                'description': u'管理员'
            },
            {
                'role_id': 3,
                'name': 'Editor',
                'description': u'编辑'
            },
            {
                'role_id': 4,
                'name': 'Author',
                'description': u'作者'
            },
            {
                'role_id': 5,
                'name': 'Reader',
                'description': u'读者'
            }
        ]

        # 创建唯一索引键
        mongo.db.roles.create_index([("role_id", flask_pymongo.ASCENDING), ("name", flask_pymongo.ASCENDING)], unique=True)

        try:
            mongo.db.roles.insert_many(roles)
        except Exception:
            pass

    @staticmethod
    def get_role_id(role):
        """
        根据角色查询角色 id
        :param role: 用户角色 Owner/Administrator/Editor/Author/Reader
        :return: 角色 id or None
        """
        roles = ['Owner', 'Administrator', 'Editor', 'Author', 'Reader']
        try:
            roles.index(role)
            return mongo.db.roles.find_one({'name': role}).get('role_id', None)
        except:
            return None

    @staticmethod
    def get_role_name(role_id):
        """
        根据角色 id 查询角色
        :param role_id: 用户角色 id 1/2/3/4/5
        :return: 角色 or None
        """
        try:
            result = mongo.db.roles.find_one({'role_id': role_id})
            return result.get('name', None)
        except:
            return None

    ##
    # 权限判断
    ##
    def can(self, permission):
        """
        判断该角色是否拥有某个权限
        :param permission: 权限
        :return: 拥有对应权限返回 True,否则返回 False
        """
        permissions = PermissionsRoles.get_role_permissions(self.role_id)
        if not permissions:
            return False
        try:
            index = permissions.index(permission)
            return index >= 0
        except:
            return False
