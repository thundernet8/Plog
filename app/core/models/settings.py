# coding=utf-8

import time
import flask_pymongo

from app import mongo


class Setting(object):
    """
    程序配置表
    :_id 自动主键
    :key 设置项
    :value 设置值
    :type 设置类型
    :create_at 设置创建时间戳
    :update_at 设置更新时间戳
    """

    def __init__(self):
        pass

    @staticmethod
    def insert_default_settings():
        """
        插入默认设置
        :return:
        """

        # 创建唯一索引键
        mongo.db.settings.create_index([("key", flask_pymongo.ASCENDING)], unique=True)

    @staticmethod
    def update_setting(key, value, type='blog'):
        """
        更新设置项或新建设置项(若不存在)
        :param key: 设置项,唯一
        :param value: 设置值
        :param type: 设置类型 core/blog/theme
        :return:
        """
        if not value:
            return False
        try:
            mongo.db.settings.update({
                'key': key,
                'value': value,
                'type': type,
                'update_at': int(time.time())
            }, {'$setOnInsert': {
                'create_at': int(time.time())
            }}, upsert=True)
            return True
        except Exception:
            return False
        return False

    @staticmethod
    def get_setting(key):
        """
        获取设置值
        :param key: 设置项
        :return: 设置值 or None
        """
        return mongo.db.settings.find({"key": key})
