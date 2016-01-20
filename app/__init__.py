# coding=utf-8

from flask import Flask
from flask.ext.pymongo import PyMongo
from flask.ext.login import LoginManager
from flask.ext.pagedown import PageDown
from flask.ext.mail import Mail

from config import config


mongo = PyMongo()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
pagedown = PageDown()
mail = Mail()


def create_app(config_name):
    """
    u根据配置创建 app
    :param config_name:
    :return:
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    mongo.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)
    mail.init_app(app)

    # 引入蓝本
    from .core.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')
