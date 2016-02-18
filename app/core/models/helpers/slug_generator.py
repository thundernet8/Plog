# coding=utf-8

import re
import unicodedata
import jieba
from slugify import slugify
import pypinyin


re_en = re.compile(r'([a-zA-Z\']+)')
re_all_en = re.compile(r'^([a-zA-Z\']+)$')
re_chinese = re.compile(ur'([\u2e80-\u9fff]+)')
re_all_chinese = re.compile(ur'^([\u2e80-\u9fff]+)$')


def get_slug(text, delimiter=u"-"):
    """
    别名生成器,将中文等字符转成拼音等 url 友好的字符串,英文保持不变
    :param text 待转换文本
    :param delimiter 文本连接符
    """
    if not text:
        return ''
    if not type(text) == unicode:
        text = text.decode('utf-8')
        # raise ValueError('should be unicode')
    slug_list = []
    segments_split_by_space = text.split()
    segments_split_by_chinese = []
    for segment in segments_split_by_space:
        segments_split_by_chinese.extend(re_chinese.split(segment))
    for segment in segments_split_by_chinese:
        if not segment:
            continue
        segment = segment.strip()
        if not segment:
            continue
        elif re_all_en.match(segment):
            slug_list.append(segment)
        elif re_all_chinese.match(segment):
            sig_list = jieba.cut(segment, cut_all=False)
            for sig in sig_list:
                arr_pinyin = sum(pypinyin.pinyin(sig, pypinyin.NORMAL), [])
                pinyin = "".join([pinyin.lower()
                                  for pinyin in arr_pinyin])
                slug_list.append(pinyin)
        else:
            slug_list.append(slugify(segment))
    slugged = delimiter.join(slug_list)
    slugged = unicode(
        unicodedata.normalize('NFKD', slugged).encode('ascii', 'ignore')
    )
    slugged = re.sub(
        r"[^\w\s%s']" % re.escape(delimiter),
        '',
        slugged
    ).strip()
    slugged = re.sub(r'[%s\s]+' % delimiter, delimiter, slugged)
    return unicode(slugged)
