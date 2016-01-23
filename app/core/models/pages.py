# coding=utf-8

from .posts import Post


class Page(Post):
    """
    页面模型,继承Post模型,共用 posts collection
    :page 是否页面,默认1
    """

    def __init__(self):
        """
        页面实例化
        :return:
        """
        super(Page, self).__init__()
        self.page = 1
