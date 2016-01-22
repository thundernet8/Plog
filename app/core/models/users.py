# coding=utf-8

import time
from datetime import datetime
from bson.objectid import ObjectId
import hashlib

import flask_pymongo
from flask import current_app
from flask.ext.login import UserMixin
from flask.ext.login import AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from app import mongo
from app import login_manager


class User(UserMixin):
    """
    用户模型
    :_id 用户 id
    :uid 用户 id(alias _id)
    :name 用户名
    :nickname 昵称
    :password 用户密码
    :email 用户邮箱
    :avatar 头像
    :cover 个人主页封面
    :bio 个人介绍
    :website 个人网站
    :location 地理位置
    :status 用户状态(banned/active, default:active)
    :confirmed 用户邮箱确认状态(1/0, default:0)
    :meta_title 个性短语
    :create_at 注册时间
    :last_login 上次登录
    :update_at 更新时间
    """

    def __init__(self, **kwargs):
        """
        获得一个用户实例
        :param kwargs: 用户筛选参数(key-value pairs)
        :return: 用户实例
        """
        super(User, self).__init__(**kwargs)
        user = mongo.db.users.find_one(dict(**kwargs))
        if user:
            self.uid = str(user.get('_id'))
            self.name = user.get('name')
            self.nickname = user.get('nickname')
            self.email = user.get('email')
            self.password = user.get('password')
            self.avatar_hash = user.get('avatar_hash')
            self.cover = user.get('cover')
            self.bio = user.get('bio')
            self.website = user.get('website')
            self.location = user.get('location')
            self.status = user.get('status')
            self.confirmed = user.get('confirmed')
            self.meta_title = user.get('meta_title')
            self.create_at = datetime.fromtimestamp(int(user.get('create_at', 0)))
            self.last_login = datetime.fromtimestamp(int(user.get('last_login', 0)))
            self.update_at = datetime.fromtimestamp(int(user.get('update_at', 0)))

    def get_id(self):
        """
        覆盖UserMixin的同名方法,使之捕获正确字段作为用户 id
        :return:
        """
        try:
            return str(self.uid)
        except AttributeError:
            raise NotImplementedError('No `uid` attribute')

    @property
    def raw_password(self):
        """
        原始密码,禁止直接读取
        :return: AttributeError
        """
        raise AttributeError('password is not a readable attribute')

    @raw_password.setter
    def raw_password(self, password):
        """
        密码 setter,将原始密码哈希后存储数据库
        :param password: 提交的原始密码
        :return:
        """
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        """
        验证密码
        :param password: 待验证密码
        :return: 成功返回 True,否则返回 False
        """
        return check_password_hash(self.password, password)

    ##
    # 用户操作
    ##
    def generate_confirmation_token(self, expiration=3600):
        """
        生成用于用户邮件确认 token
        :param expiration: token 过期时间
        :return: token 字符串
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm_uid': self.uid}).decode('ascii')

    def confirm(self, token):
        """
        用户确认
        :param token: 用于确认的 token
        :return: 成功返回 True,否则返回 False
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm_uid') != self.uid:
            return False
        self.confirmed = 1
        mongo.db.users.update_one({
            '_id': ObjectId(self.uid)
        }, {
            '$set': {
                'confirmed': 1
            }
        })
        return True

    def generate_reset_token(self, expiration=3600):
        """
        生成用于重置密码的 token
        :param expiration: token 过期时间
        :return: token 字符串
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset_uid': self.uid}).decode('ascii')

    def reset_user_password(self, token, new_password):
        """
        重置用户密码
        :param token: 用于验证的 token
        :param new_password: 新密码
        :return: 成功返回 True,否则返回 False
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_uid') != self.uid:
            return False
        self.raw_password = new_password
        mongo.db.users.update_one({
            '_id': ObjectId(self.uid)
        }, {
            '$set': {
                'password': self.password
            }
        })
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        """
        生成用于重置密码的 token
        :param new_email: 新的邮箱地址
        :param expiration: token 过期时间
        :return: token 字符串
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'reset_uid': self.uid, 'new_email': new_email}).decode('ascii')

    def change_user_email(self, token):
        """
        重置用户邮箱
        :param token: 用于验证的 token
        :return:  成功返回 True,否则返回 False
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset_uid') != self.uid:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if mongo.db.users.find_one({'email': new_email}):
            return False  # 邮箱已存在
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        mongo.db.users.update_one({
            '_id': ObjectId(self.uid)
        }, {
            '$set': {
                'avatar_hash': self.avatar_hash
            }
        })
        return True

    ##
    # 用户属性
    ##
    def can(self, permissions):
        """
        判断用户是否拥有对应权限
        :param permissions: 用户权限
        :return: 拥有对应权限返回 True,否则返回False
        """
        # TODO 待添加权限模型后更新
        pass

    def is_administrator(self):
        """
        判断用户是否管理员(网站拥有者也是管理员)
        :return: 是则返回 True,否则返回 False
        """
        # TODO 待添加权限模型后更新
        pass

    def get_avatar(self, size=100, default='identicon', rating='g'):
        """
        获取用户通用头像
        :param size: 头像尺寸,长宽一致
        :param default: Gravatar头像类型
        :param rating: Gravatar 头像分级
        :return: Gravatar 头像链接
        """
        url = 'https://secure.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default,
                                                                     rating=rating)

    ##
    # 用户查询&数据库操作
    ##
    @staticmethod
    def get_user_by_field(field, value):
        """
        通过字段值获取用户实例
        :param field: 用户数据库字段(id/email/name)
        :param value: 字段值
        :return: 用户实例 or None
        """
        valid_fields = ['id', 'name', 'email']
        if field not in valid_fields:
            return None
        if field == 'id':
            field = '_id'
            value = ObjectId(value)
        return User(field=value)

    @staticmethod
    def create_table_indexes():
        """
        创建数据库若干字段唯一索引,程序部署初始化调用
        :return:
        """
        mongo.db.settings.create_index([("name", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.settings.create_index([("email", flask_pymongo.ASCENDING)], unique=True)
