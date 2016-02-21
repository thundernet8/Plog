# coding=utf-8

import unittest

from app import create_app

from app.core.models.comments import Comment
from app.core.models.comments import Comments


class CommentsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')  # TODO add test config
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_add_comment(self):
        cid = Comment.add_comment(post_id=9, user_id=3, parent=0,
                                  content=u'中国银行业大举引进外界，低价抛售股权的时代已经过去', approved=1)
        self.assertTrue(cid, msg=u'插入评论成功')

    def test_pagination(self):
        # pagenation = Comments(filters={'approved': 1}).pagination(page=1)
        # self.assertTrue(pagenation, msg=u'获取分页模型成功')
        pass
