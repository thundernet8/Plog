# coding=utf-8

from math import ceil


class Pagination(object):
    """
    集合分页工具(如 posts/comments 等)
    """

    def __init__(self, query_class, per_page, page, total, items, filters, order_by, order):
        """
        初始化
        :param query_class: 集合类(Post/Comment)
        :param page: 分页页码
        :param per_page: 每页显示数量
        :param total: 未分页集合全部数量
        :param items: 集合数组(posts/comments)
        :param filters: 过滤器
        :param order_by: 排序依据
        :param order: 升/降序
        :return:
        """
        self.query_class = query_class
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items
        self.filters = filters
        self.order_by = order_by
        self.order = order

    @property
    def pages(self):
        """
        总页数
        :return: 总的页数
        """
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        """
        上一页的分页模型
        :param error_out: 是否显示错误信息
        :return: 上一页的 Pagination 对象
        """
        return self.query_class.get_pagination(self.per_page, self.page - 1, self.filters, self.order_by,
                                               self.order, error_out)

    @property
    def prev_num(self):
        """
        获取上一页页码
        :return: 上一页页码
        """
        return self.page - 1

    @property
    def has_prev(self):
        """
        判断是否存在上一页
        :return: 存在上一页则返回 True,否则返回 False
        """
        return self.page > 1

    def next(self, error_out=False):
        """
        下一页的分页模型
        :param error_out: 是否显示错误信息
        :return: 下一页的 Pagination 对象
        """
        return self.query_class.get_pagination(self.per_page, self.page + 1, self.filters, self.order_by,
                                               self.order, error_out)

    @property
    def next_num(self):
        """
        获取下一页页码
        :return: 下一页页码
        """
        return self.page + 1

    @property
    def has_next(self):
        """
        判断是否存在下一页
        :return: 存在下一页则返回 True,否则返回 False
        """
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """
        页码迭代器,页码数过多时,部分省略,当前左边开始至多显示left_edge个页码,当前页码的相邻左边至多显示 left_current个页码,右边同此
        :param left_edge: 左端至多显示连续页码数
        :param left_current: 当前页相邻左边至多显示连续页码数
        :param right_current: 当前页相邻右边至多显示连续页码数
        :param right_edge: 右端至多显示连续页码数
        :return:
        """
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or (num > self.page - left_current- 1 and num < self.page + right_current)\
                    or num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num