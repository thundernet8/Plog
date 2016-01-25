# coding=utf-8

import pymongo

from app import mongo


def add_mongo_counters():
    """
    为MongoDB 添加专用自增序列尾值记录表
    :return:
    """
    mongo.db.counters.insert_many([
        {'table_field': 'user_id', 'seq': 0},
        {'table_field': 'post_id', 'seq': 0},
        {'table_field': 'tag_id', 'seq': 0},
        {'table_field': 'comment_id', 'seq': 0},
    ])


def get_next_sequence(field):
    """
    获取表的自增字段的下一个序列数字
    :param field: 自增字段
    :return: 序列数字
    """
    ret = mongo.db.counters.find_one_and_update({
        {'table_field': field},
        {'$inc': {'seq': 1}}
    }, upsert=True, return_document=pymongo.ReturnDocument.AFTER)

    return ret.get('seq')
