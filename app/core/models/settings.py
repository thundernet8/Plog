# coding=utf-8

import time
import flask_pymongo
from bson.objectid import ObjectId
import json

from flask import url_for

from app import mongo


class Setting(object):
    """
    程序配置表
    :_id 自动主键
    :setting_name 设置名
    :setting_value 设置值
    :type 设置类型
    :create_at 设置创建时间戳
    :update_at 设置更新时间戳
    """

    def __init__(self, setting_name):
        """
        返回一个设置项实例
        :param setting_name: 设置名
        :return: 一个设置项实例
        """
        self.setting_name = setting_name
        self.setting_value = Setting.get_setting(setting_name)

    @staticmethod
    def insert_default_settings():
        """
        插入默认设置
        :return:
        """
        # 创建唯一索引键
        mongo.db.settings.create_index([("setting_name", flask_pymongo.ASCENDING)], unique=True)

        # 每页文章数
        Setting.update_setting('posts_per_page', 10, 'blog')
        # 每页评论数
        Setting.update_setting('comments_per_page', 20, 'blog')
        # 默认导航
        Setting.update_setting('navigation', json.dumps({'navigations': [{u'首页': url_for('main.index', _external=True)}]}))
        # navigations structure #
        # {'navigations': [
        #     {'primary': {u'首页': '/'}},
        #     {'primary': {u'文章': '/blog'}, 'sub': [
        #         {'subTitle1': '/link1'},
        #         {'subTitle2': '/link2'}
        #     ]}
        # ]}

    @staticmethod
    def update_setting(setting_name, setting_value, type='blog'):
        """
        更新设置项或插入设置项(若不存在)
        :param setting_name: 设置名,唯一
        :param setting_value: 设置值
        :param type: 设置类型 core/blog/theme, 默认blog
        :return: 成功返回True,失败返回False
        """
        if not setting_value:
            return False
        try:
            result = mongo.db.settings.update_one({
                'setting_name': setting_name
            }, {'$set': {
                'setting_value': setting_value,
                'type': type,
                'update_at': int(time.time())
            }, '$setOnInsert': {
                'create_at': int(time.time())
            }}, upsert=True)
            if result and (result.modified_count or result.upserted_id):
                return True
        except Exception:
            return False
        return False

    @staticmethod
    def add_setting(setting_name, setting_value, type='blog'):
        """
        插入设置项(若不存在)
        :param setting_name: 设置名,唯一
        :param setting_value: 设置值
        :param type: 设置类型 core/blog/theme, 默认blog
        :return: 成功返回True,失败返回False
        """
        return Setting.update_setting(setting_name, setting_value, type)

    @staticmethod
    def get_setting(setting_name, default=None, record=False):
        """
        获取设置值
        :param setting_name: 设置名
        :param default: 默认值
        :param record: 是否返回整条记录,如果为True,返回 dict 形式整条记录,否则返回设置值
        :return: 设置值/记录 or None
        """
        result = mongo.db.settings.find_one({"setting_name": setting_name})
        if not result:
            return default
        if record:
            return result
        return result.get('setting_value', default)

    @staticmethod
    def get_settings(setting_names, record=False):
        """
        获取多个设置值
        :param setting_names: 设置名组成的数组
        :param record: 是否返回完整记录,如果为True,返回包含 dict 形式记录的数组,否则返回设置值组成的数组
        :return: 设置值/记录的字典 or None
        """
        if not isinstance(setting_names, list):
            return None
        results = mongo.db.settings.find({"setting_name": {"$in": setting_names}})
        if not results or results.count() == 0:
            return None
        if record:
            records = {}
            for result in results:
                records[result.get('setting_name', 'err_name')] = result.get('setting_value')
            return records
        values = {}
        for result in results:
            values[result.get('setting_name', 'err_name')] = result.get('setting_value')
        return values

    @staticmethod
    def delete_setting(setting_name):
        """
        删除设置项
        :param setting_name: 设置名
        :return: 删除成功返回True,否则返回False
        """
        deletes = mongo.db.settings.delete_many({'setting_name': setting_name})
        if deletes and deletes.deleted_count > 0:
            return True
        # TODO 添加类型错误,指示该设置不存在或者是删除失败
        return False

    def __repr__(self):
        return '<Setting instance: %r>' % self.setting_name
