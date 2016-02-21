# coding=utf-8

import functools
import urllib
import hashlib
from datetime import datetime

from flask import current_app
from flask import request
from jinja2 import nodes
from jinja2.ext import Extension
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import redis


def redis_cached(timeout=None, key_prefix='view/%s', unless=None):
    """
    路由视图缓存装饰器
    :param timeout: 缓存过期时间, 如果不设置则默认3600秒
    :param key_prefix: 缓存键
    :param unless: 条件判断是否跳过缓存
    :return: 缓存的或实时的视图内容
    """
    def decorator(f):
        @functools.wraps(f)  # 复制函数信息
        def decorated_function(*args, **kwargs):
            if callable(unless) and unless() is True:
                return f(*args, **kwargs)

            if kwargs.get('nocache'):
                return f(*args, **kwargs)  # 当被装饰函数中包含 nocache 参数时跳过缓存

            try:
                cache_key = decorated_function.make_cache_key(*args, **kwargs)
                cache_key = urllib.quote(cache_key, safe='')
                rv = redis_get(cache_key)
            except Exception:
                if current_app.debug:
                    raise
                return f(*args, **kwargs)

            if rv is None:
                rv = f(*args, **kwargs)
                try:
                    redis_set(cache_key, rv, timeout=decorated_function.cache_timeout)
                except Exception:
                    if current_app.debug:
                        raise
                    return f(*args, **kwargs)
            return rv

        def make_cache_key(*args, **kwargs):
            if callable(key_prefix):
                cache_key = key_prefix()
            elif '%s' in key_prefix:
                cache_key = key_prefix % request.url
            else:
                cache_key = key_prefix
            cache_key = hashlib.md5(cache_key.encode('utf-8')).hexdigest()
            cache_key = '_'.join((get_version(level='day'), cache_key))
            return cache_key

        decorated_function.uncached = f
        decorated_function.cache_timeout = timeout
        decorated_function.make_cache_key = make_cache_key

        return decorated_function
    return decorator


def redis_memoize(timeout=100, make_name=None, unless=None):
    """
    函数结果记忆装饰器
    :param timeout: 记忆过期时间, 默认100s
    :param make_name: 一个函数,接收被装饰函数的函数名,可生成更独特的新函数名,用做缓存键的一部分,防止缓存键重复的可能
    :param unless: 条件判断是否跳过缓存
    :return: 缓存的或实时的函数结果
    """
    def decorator(f):
        @functools.wraps(f)  # 复制函数信息
        def decorated_function(*args, **kwargs):
            if callable(unless) and unless() is True:
                return f(*args, **kwargs)

            if kwargs.get('nocache'):
                return f(*args, **kwargs)  # 当被装饰函数中包含 nocache 参数时跳过缓存

            try:
                cache_key = decorated_function.make_cache_key(make_name, args, kwargs)
                rv = redis_get(cache_key)
            except Exception:
                if current_app.debug:
                    raise
                return f(*args, **kwargs)

            if rv is None:
                rv = f(*args, **kwargs)
                try:
                    redis_set(cache_key, rv, timeout=decorated_function.cache_timeout)
                except Exception:
                    if current_app.debug:
                        raise
                    return f(*args, **kwargs)
            return rv

        def make_cache_key(make_name, keyargs, keykwargs):
            fname = f.__name__
            if callable(make_name):
                fname = make_name(fname)
            if isinstance(make_name, str):
                fname = make_name
            alt_fname = '.'.join((f.__module__, fname))
            try:
                origin_str = "{0}{1}{2}".format(alt_fname, keyargs, keykwargs)
            except AttributeError:
                origin_str = "%s%s%s" % (alt_fname, keyargs, keykwargs)
            cache_key = hashlib.md5(origin_str.encode('utf-8')).hexdigest()
            cache_key = '_'.join((get_version(level='day'), cache_key))
            return cache_key

        decorated_function.uncached = f
        decorated_function.cache_timeout = timeout
        decorated_function.make_cache_key = make_cache_key

        return decorated_function
    return decorator


def redis_get(key):
    value = redis.get(key)
    if value is not None:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(value)
            return data
        except Exception:
            return None
    return None


def redis_set(key, value, timeout=60):
    s = Serializer(current_app.config['SECRET_KEY'], timeout)
    try:
        data = s.dumps(value)
        redis.set(key, data)
        return True
    except Exception:
        return False


def get_version(level='hour'):
    """
    获取以日期时间生成的版本号,版本号作为缓存键的起始字符,可用于批量删除某天/小时/分钟内的缓存
    :param level: 精确的等级, minute精确到分钟,hour精确到小时,day精确到天
    :return:
    """
    format_str = '%Y%m%d%H'
    if level == 'minute':
        format_str == '%Y%m%d%H%M'
    elif level == 'day':
        format_str == '%Y%m%d'
    version = datetime.today().strftime(format_str)
    return version


def redis_clear_cache(key=None):
    pass  # TODO clear cache


class JinjaCacheExtension(Extension):
    """
    扩展Jinja2,添加 cache 标签支持, 以缓存模板分段内容, 来自Flask-Cache
    """
    tags = set(['cache'])

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        args = [parser.parse_expression()]  # 解析标签参数,包括 timeout
        if parser.stream.skip_if('comma'):
            args.append(parser.parse_expression())
        else:
            args.append(nodes.Const('%s%s' % (parser.filename, lineno)))
        vary_on = []
        while parser.stream.skip_if('comma'):
            vary_on.append(parser.parse_expression())

        if vary_on:
            args.append(nodes.List(vary_on))
        else:
            args.append(nodes.Const([]))

        body = parser.parse_statements(['name:endcache'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_cache', args), [], [], body).set_lineno(lineno)

    def _cache(self, timeout, fragment_name, vary_on, caller):
        if vary_on:
            fragment_name = '%s_' % fragment_name
        key_suffix = '%s%s' % (fragment_name, "_".join(vary_on))
        key_suffix = hashlib.md5(key_suffix.encode('utf-8')).hexdigest()
        key = '_template_fragment_cache_%s' % key_suffix

        if timeout == 'del':
            redis_clear_cache(key)
            return caller()

        rv = redis_get(key)
        if rv is None:
            rv = caller()
            redis_set(key, rv, timeout)
        return rv


class JinjaCache(object):

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.jinja_env.add_extension(JinjaCacheExtension)
