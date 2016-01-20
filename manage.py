#!/usr/bin/env python
# coding=utf-8

import os

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


from app import create_app
from flask.ext.script import Manager, Shell

# 创建App
app = create_app(os.getenv('PLOG_CONFIG') or 'default')
manager = Manager(app)


# Manager Script上下文
def make_shell_context():
    return dict(app=app)
manager.add_command('shell', Shell(make_context=make_shell_context()))


@manager.command
def deploy():
    """
    执行部署任务
    :return:
    """

    pass


if __name__ == '__main__':
    manager.run()
