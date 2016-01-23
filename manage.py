#!/usr/bin/env python
# coding=utf-8

import os

from flask.ext.script import Manager
from flask.ext.script import Shell

from app import create_app
from app import mongo
from app import login_manager
from app import mail
from app.core.models.roles import Role
from app.core.models.settings import Setting
from app.core.models.users import User

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
manager = Manager(app)


# Manager Script上下文
def make_shell_context():
    return dict(app=app, mongo=mongo, login_manager=login_manager, mail=mail, Role=Role, Setting=Setting, User=User)
manager.add_command('shell', Shell(make_context=make_shell_context))


@manager.command
def deploy():
    """
    执行部署任务
    :return:
    """

    # 插入默认角色
    Role.insert_default_roles()


@manager.command
def test():
    pass


if __name__ == '__main__':
    manager.run()
