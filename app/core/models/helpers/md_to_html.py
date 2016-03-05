# coding=utf-8

from markdown import markdown
import bleach


def parse_markdown(md):
    """
    解析 markdown 为 html
    :param md: markdown 文档
    :return: html 文档
    """
    allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']
    if not md:
        return ''
    html = bleach.linkify(bleach.clean(markdown(md, output_format='html'), tags=allowed_tags))
    return html
