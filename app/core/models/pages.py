# coding=utf-8

from .posts import Post
from .posts import Posts


class Page(Post):
    """
    页面模型,继承Post模型,共用 posts collection
    :type 文章类型,默认page
    """

    def __init__(self, **kwargs):
        """
        页面实例化
        :return:
        """
        super(Page, self).__init__(**kwargs)
        self.type = kwargs.get('type', 'page')


class Pages(Posts):
    """
    文章对象数组模型,用于分页等集合查询
    """

    def __init__(self, **kwargs):
        """
        模型初始化,引入参数
        :param kwargs: 文章集合查询参数
        :return:
        """
        super(Pages, self).__init__(**kwargs)
        self.filters['type'] = 'page'
        self.page_id = self.post_id
