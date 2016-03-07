# coding=utf-8

import flask_pymongo

from app import mongo


class PermissionsRoles(object):
    """
    权限角色关系模型
    :_id 自动 id
    :role_id 角色 id
    :permission_id 权限 id
    """

    def __init__(self):
        pass

    ##
    # 数据库部署
    ##
    @staticmethod
    def create_table_indexes():
        """
        创建数据库若干字段唯一索引,程序部署初始化调用
        :return:
        """
        mongo.db.permissions_roles.create_index([("role_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.permissions_roles.create_index([("permission_id", flask_pymongo.ASCENDING)], unique=True)

    @staticmethod
    def insert_defaults_permissions_roles():
        """
        添加默认权限角色数据,网站部署初始化使用
        :return:
        """
        permissions_roles = [
            {'role_id': 1, 'permission_id': 1}, {'role_id': 1, 'permission_id': 2}, {'role_id': 1, 'permission_id': 3},
            {'role_id': 1, 'permission_id': 4}, {'role_id': 1, 'permission_id': 5}, {'role_id': 1, 'permission_id': 6},
            {'role_id': 1, 'permission_id': 7}, {'role_id': 1, 'permission_id': 8}, {'role_id': 1, 'permission_id': 9},
            {'role_id': 1, 'permission_id': 10}, {'role_id': 1, 'permission_id': 11}, {'role_id': 1, 'permission_id': 12},
            {'role_id': 1, 'permission_id': 13}, {'role_id': 1, 'permission_id': 14}, {'role_id': 1, 'permission_id': 15},
            {'role_id': 1, 'permission_id': 16}, {'role_id': 1, 'permission_id': 17}, {'role_id': 1, 'permission_id': 18},
            {'role_id': 1, 'permission_id': 19}, {'role_id': 1, 'permission_id': 20}, {'role_id': 1, 'permission_id': 21},
            {'role_id': 1, 'permission_id': 22}, {'role_id': 1, 'permission_id': 23}, {'role_id': 2, 'permission_id': 3},
            {'role_id': 2, 'permission_id': 4}, {'role_id': 2, 'permission_id': 5}, {'role_id': 2, 'permission_id': 6},
            {'role_id': 2, 'permission_id': 7}, {'role_id': 2, 'permission_id': 8}, {'role_id': 2, 'permission_id': 9},
            {'role_id': 2, 'permission_id': 10}, {'role_id': 2, 'permission_id': 11}, {'role_id': 2, 'permission_id': 12},
            {'role_id': 2, 'permission_id': 13}, {'role_id': 2, 'permission_id': 14}, {'role_id': 2, 'permission_id': 15},
            {'role_id': 2, 'permission_id': 16}, {'role_id': 2, 'permission_id': 17}, {'role_id': 2, 'permission_id': 18},
            {'role_id': 2, 'permission_id': 19}, {'role_id': 2, 'permission_id': 20}, {'role_id': 2, 'permission_id': 21},
            {'role_id': 2, 'permission_id': 22}, {'role_id': 2, 'permission_id': 23}, {'role_id': 3, 'permission_id': 7},
            {'role_id': 3, 'permission_id': 8}, {'role_id': 3, 'permission_id': 9}, {'role_id': 3, 'permission_id': 10},
            {'role_id': 3, 'permission_id': 11}, {'role_id': 3, 'permission_id': 12}, {'role_id': 3, 'permission_id': 13},
            {'role_id': 3, 'permission_id': 14}, {'role_id': 3, 'permission_id': 16}, {'role_id': 3, 'permission_id': 17},
            {'role_id': 3, 'permission_id': 18}, {'role_id': 3, 'permission_id': 19}, {'role_id': 4, 'permission_id': 7},
            {'role_id': 4, 'permission_id': 9}, {'role_id': 4, 'permission_id': 10}, {'role_id': 4, 'permission_id': 13},
            {'role_id': 4, 'permission_id': 19}, {'role_id': 5, 'permission_id': 7}
        ]
        try:
            mongo.db.permissions_roles.insert_many(permissions_roles)
        except Exception:
            pass

    ##
    # 查询
    ##
    @staticmethod
    def get_role_permissions(role_id):
        """
        获取角色的所有权限
        :param role_id: 角色 id
        :return: 权限列表 or None
        """
        try:
            results = mongo.db.permissions_roles.find(
                    {'role_id': role_id}, {'permission_id': flask_pymongo.ASCENDING, '_id': 0}
            )
            if not results or results.count() == 0:
                return None
        except:
            return None
        permission_ids = []
        for result in results:
            permission_ids.append(result.get('permission_id'))
        try:
            results = mongo.db.permissions.find({'permission_id': {'$in': permission_ids}},
                                                {'name': flask_pymongo.ASCENDING, '_id': 0})
            if not results:
                return None
            permissions = []
            for result in results:
                permissions.append(result.get('name'))
            return permissions
        except:
            return None
