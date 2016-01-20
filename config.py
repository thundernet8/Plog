# coding=utf-8
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    基本配置
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'auoV1qiXG7tPz9IFhvge'

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    PLOG_SLOW_DB_QUERY_TIME = 0.5

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    """
    开发配置
    """
    DEBUG = True

    # db config
    MONGO_HOST = 'http://localhost'
    MONGO_PORT = 27017
    MONGO_DBNAME = 'Plog-Dev'
    MONGO_USERNAME = 'root'
    MONGO_PASSWORD = 'root'


class DistConfig(Config):
    """
    生产配置
    """
    DEBUG = False

    # db config
    MONGO_HOST = 'http://localhost'
    MONGO_PORT = 27017
    MONGO_DBNAME = 'Plog'
    MONGO_USERNAME = None
    MONGO_PASSWORD = None


config = {
    'development': DevConfig,
    'distribution': DistConfig,
    'default': DevConfig
}
