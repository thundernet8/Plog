# coding=utf-8

import unittest

from app import create_app

from app.core.models.posts import Post
from app.core.models.posts import Posts


class PostsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('development')  # TODO add test config
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_add_post(self):
        # pid = Post.draft_post(title=u'研究表明：单身汪要想快速脱单，就该多上网！', slug=u'tuo-dan3',
        #                 html=u'<p>情人节，哦不，虐狗节刚刚过去，但是虎嗅君欣慰地发现，今年票圈里除了秀恩爱的情侣，还出现了这样的图：</p>',
        #                 status='published', author_id=3, create_at=1455711409, comment_count=5, view_count=90)
        # if pid:
        #     pid = Post.publish_post(pid)
        # self.assertTrue(pid, msg=u'插入草稿并发布成功')
        pass

    def test_pagination(self):
        # pagenation = Posts(filters={'status': 'published'}).pagination(page=1)
        # self.assertTrue(pagenation, msg=u'获取分页模型成功')
        pass
