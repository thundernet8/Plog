#!/usr/bin/env python
# coding=utf-8

import os
from datetime import datetime
import json

from flask import Markup
from flask import render_template
from flask.ext.script import Manager
from flask.ext.script import Shell

from app import create_app
from app import mongo
from app import login_manager
from app import mail
from app import redis
from app.core.models.roles import Role
from app.core.models.settings import Setting
from app.core.models.users import User
from app.core.models.posts import Post
from app.core.models.posts import Posts
from app.core.models.pages import Page
from app.core.models.pages import Pages
from app.core.models.permissions import Permission
from app.core.models.permissions_roles import PermissionsRoles
from app.core.models.tags import Tag
from app.core.models.comments import Comment
from app.core.models.comments import Comments
from app.core.models.mongo_counter import add_mongo_counters

# 启用覆盖测试
COV = None
if os.environ.get('PG_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

# 导入.env内的环境配置
if os.path.exists('.env'):
    print "Importing environment vars from .env"
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]


# 创建App
app = create_app(os.getenv('PLOG_CONFIG') or 'default')


# 错误处理 # 蓝本不支持404和500的处理方法
@app.errorhandler(404)
def app_404(e):
    return render_template('error_pages/404.html'), 404


@app.errorhandler(500)
def app_500(e):
    return render_template('error_pages/500.html'), 500

# jinja_env
app.jinja_env.globals['Setting'] = Setting
app.jinja_env.globals['User'] = User
app.jinja_env.globals['Post'] = Post
app.jinja_env.globals['datetime'] = datetime
app.jinja_env.globals['json'] = json
app.jinja_env.globals['str'] = str
app.jinja_env.globals['Markup'] = Markup

manager = Manager(app)


# Manager Script上下文
def make_shell_context():
    return dict(app=app, mongo=mongo, login_manager=login_manager, mail=mail, redis=redis, Role=Role, Setting=Setting,
                User=User, Post=Post, Posts=Posts, Page=Page, Pages=Pages, Permission=Permission,
                PermissionsRoles=PermissionsRoles, Tag=Tag, Comment=Comment, Comments=Comments)
manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def deploy():
    """
    执行部署任务
    :return:
    """

    # 清空数据库
    # TODO

    # 为MongoDB 添加专用自增序列尾值记录表
    add_mongo_counters()
    # 默认角色添加
    Role.insert_default_roles()
    # 权限数据库索引与默认数据添加
    Permission.create_table_indexes()
    Permission.insert_defaults_permissions()
    # 权限角色关系数据库索引与默认数据添加
    PermissionsRoles.create_table_indexes()
    PermissionsRoles.insert_defaults_permissions_roles()
    # 文章数据库索引
    Post.create_table_indexes()
    # 用户数据库索引
    User.create_table_indexes()
    # 设置数据库索引与默认数据添加
    Setting.insert_default_settings()
    # 标签数据库索引
    Tag.create_table_indexes()
    # 评论数据库索引
    Comment.create_table_indexes()
    # 用户数据库索引
    User.create_table_indexes()


@manager.command
def test(coverage=False):
    """
    测试
    :param coverage 是否启用覆盖测试
    :return:
    """
    if coverage and not os.environ.get('PG_COVERAGE'):
        import sys
        os.environ['PG_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tests/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == '__main__':
    manager.run()
