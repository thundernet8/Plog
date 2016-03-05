# coding=utf-8

import flask_pymongo

from app import mongo
from .tags import Tag


class PostsTags(object):
    """
    标签文章关系模型
    :_id 自动 id
    :post_id 文章 id
    :tag_id 标签 id
    """

    def __init__(self):
        pass

    @staticmethod
    def get_post_tags(post_id):
        """
        获取文章的标签列表
        :param post_id: 文章 id
        :return: 文章下的标签列表 or None
        """
        tags = []
        try:
            results = mongo.db.posts_tags.find({
                'post_id': post_id
            })
            for result in results:
                tag_id = result.get('tag_id')
                tag = Tag.get_tag_by_id(tag_id)
                tags.append(tag)
            if len(tags) > 0:
                return tags
            return None
        except:
            return None

    @staticmethod
    def add_post_tags_relation(post_id, tag_ids):
        """
        添加文章与标签关联记录
        :param post_id: 文章 id
        :param tag_ids: 标签 id 列表
        :return: 添加成功返回插入的记录数量,否则返回 False
        """
        count = 0
        try:
            mongo.db.posts_tags.delete_many({'post_id': post_id})
        except:
            pass
        for tag_id in tag_ids:
            tag_id = int(tag_id)
            try:
                result = mongo.db.posts_tags.update_one({
                    'post_id': post_id, 'tag_id': tag_id
                }, {
                    '$setOnInsert': {
                        'post_id': post_id,
                        'tag_id': tag_id
                    }
                }, upsert=True)
                #count += result.modified_count or result.upserted_id
                if result.upserted_id:
                    count += 1
            except:
                pass
        return count if count else False
