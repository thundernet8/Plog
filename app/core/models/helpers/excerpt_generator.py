# coding=utf-8

import re


def get_excerpt(text, count, suffix=u'', wrapper=u'p'):
    """
    获取摘要
    :param text: 文章原文本
    :param count: 摘要最大长度
    :param suffix: 摘要前缀
    :param wrapper: 摘要外包裹标签
    :return: 摘要
    """
    if not text:
        return ''
    # assert(isinstance(text, unicode))
    if not type(text) == unicode:
        text = text.decode('utf-8')
    excerpt = re.sub(r'<.*?>', u'', text)
    excerpt = u''.join(excerpt.split())[0:count]
    return u'<{0}>{1}{2}</{0}>'.format(wrapper, excerpt, suffix)
