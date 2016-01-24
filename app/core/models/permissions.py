# coding=utf-8

import flask_pymongo

from app import mongo


class Permission(object):
    """
    权限模型
    :id 权限 id
    :name 权限名称
    :type 权限类型
    :action_type 权限操作类型
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
        mongo.db.settings.create_index([("id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.settings.create_index([("name", flask_pymongo.ASCENDING)], unique=True)

    @staticmethod
    def insert_defaults_permissions():
        """
        添加默认权限数据,网站部署初始化使用
        :return:
        """
        permissions = [
            {
                'id': 1,
                'name': 'import_db',
                'type': 'db',
                'action_type': 'importContent'
            },
            {
                'id': 2,
                'name': 'delete_db_content',
                'type': 'db',
                'action_type': 'deleteContent'
            },
            {
                'id': 3,
                'name': 'send_mail',
                'type': 'mail',
                'action_type': 'send'
            },
            {
                'id': 4,
                'name': 'read_notifications',
                'type': 'notification',
                'action_type': 'read'
            },
            {
                'id': 5,
                'name': 'add_notifications',
                'type': 'notification',
                'action_type': 'add'
            },
            {
                'id': 6,
                'name': 'delete_notifications',
                'type': 'notification',
                'action_type': 'delete'
            },
            {
                'id': 7,
                'name': 'read_posts',
                'type': 'post',
                'action_type': 'read'
            },
            {
                'id': 8,
                'name': 'edit_posts',
                'type': 'post',
                'action_type': 'edit'
            },
            {
                'id': 9,
                'name': 'edit_self_posts',
                'type': 'post',
                'action_type': 'edit'
            },
            {
                'id': 10,
                'name': 'add_posts',
                'type': 'post',
                'action_type': 'add'
            },
            {
                'id': 11,
                'name': 'publish_posts',
                'type': 'post',
                'action_type': 'add'
            },
            {
                'id': 12,
                'name': 'delete_posts',
                'type': 'post',
                'action_type': 'delete'
            },
            {
                'id': 13,
                'name': 'delete_self_posts',
                'type': 'post',
                'action_type': 'delete'
            },
            {
                'id': 14,
                'name': 'read_settings',
                'type': 'setting',
                'action_type': 'read'
            },
            {
                'id': 15,
                'name': 'edit_setting',
                'type': 'setting',
                'action_type': 'edit'
            },
            {
                'id': 16,
                'name': 'edit_tags',
                'type': 'tag',
                'action_type': 'edit'
            },
            {
                'id': 17,
                'name': 'add_tags',
                'type': 'tag',
                'action_type': 'add'
            },
            {
                'id': 18,
                'name': 'delete_tags',
                'type': 'tag',
                'action_type': 'delete'
            },
            {
                'id': 19,
                'name': 'read_users',
                'type': 'user',
                'action_type': 'read'
            },
            {
                'id': 20,
                'name': 'edit_users',
                'type': 'user',
                'action_type': 'edit'
            },
            {
                'id': 21,
                'name': 'ban_users',
                'type': 'user',
                'action_type': 'edit'
            },
            {
                'id': 22,
                'name': 'add_users',
                'type': 'user',
                'action_type': 'add'
            },
            {
                'id': 23,
                'name': 'delete_users',
                'type': 'user',
                'action_type': 'delete'
            }
        ]
        try:
            mongo.db.permissions.insert_many(permissions)
        except Exception:
            pass
