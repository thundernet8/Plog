# coding=utf-8

import functools
import urllib

from flask import current_app
from flask import request
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app import redis


def redis_cached(timeout=None, key_prefix='view/%s', never=None):
    """
    路由视图缓存装饰器
    :param timeout: 缓存过期时间
    :param key_prefix: 缓存键
    :param never: 是否跳过缓存
    :return: 缓存的或实时的视图内容
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if callable(never) and never() is True:
                return f(*args, **kwargs)

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
