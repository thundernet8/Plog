# coding=utf-8

import time
from datetime import datetime
from bson.objectid import ObjectId
import hashlib

import flask_pymongo
from flask import current_app
from flask import url_for
from flask.ext.login import UserMixin
from flask.ext.login import AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from app import mongo
from app import login_manager
from .roles import Role
from .posts import Post
from .comments import Comment
from .mongo_counter import get_next_sequence


class User(UserMixin):
    """
    用户模型
    :user_id 用户 id
    :name 用户名
    :nickname 昵称
    :password 用户密码
    :email 用户邮箱
    :role_id 角色 id,默认5,即读者
    :avatar_hash Gravatar头像哈希值
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

    ##
    # 数据库部署
    ##
    @staticmethod
    def create_table_indexes():
        """
        创建数据库若干字段唯一索引,程序部署初始化调用
        :return:
        """
        mongo.db.users.create_index([("user_id", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.users.create_index([("name", flask_pymongo.ASCENDING)], unique=True)
        mongo.db.users.create_index([("email", flask_pymongo.ASCENDING)], unique=True)

    ##
    # 用户实例
    #
    def __init__(self, **kwargs):
        """
        获得一个用户实例
        :param kwargs: 用户筛选参数(key-value pairs)
        :return: 用户实例
        """
        # super(User, self).__init__(**kwargs)
        user = mongo.db.users.find_one(dict(kwargs))
        if user:
            self.user_id = int(user.get('user_id'))
            self.name = user.get('name')
            self.nickname = user.get('nickname') or self.name
            self.email = user.get('email')
            self.password = user.get('password')
            self.role_id = user.get('role_id') or 5
            self.avatar_hash = user.get('avatar_hash') or hashlib.md5(self.email.encode('utf-8')).hexdigest()
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
        else:
            self.user_id = None

    def get_id(self):
        """
        覆盖UserMixin的同名方法,使之捕获正确字段作为用户 id
        :return:
        """
        try:
            return int(self.user_id)
        except AttributeError:
            raise NotImplementedError('No `user_id` attribute')

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
        # mongo.db.users.update_one({
        #     'user_id': self.user_id
        # }, {
        #     '$set': {
        #         'password': self.password
        #     }
        # })

    def verify_password(self, password):
        """
        验证密码
        :param password: 待验证密码
        :return: 成功返回 True,否则返回 False
        """
        return check_password_hash(self.password, password)

    ##
    # 用户个人操作
    ##
    def generate_confirmation_token(self, expiration=3600):
        """
        生成用于用户邮件确认 token
        :param expiration: token 过期时间
        :return: token 字符串
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm_uid': self.user_id}).decode('ascii')

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
        if data.get('confirm_uid') != self.user_id:
            return False
        self.confirmed = 1
        mongo.db.users.update_one({
            'user_id': self.user_id
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
        return s.dumps({'reset_uid': self.user_id, 'email': self.email}).decode('ascii')

    @staticmethod
    def reset_user_password(token, new_password):
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
        user = User(email=data.get('email'))
        if not user or not user.user_id:
            return False
        if data.get('reset_uid') != user.user_id:
            return False
        user.raw_password = new_password
        mongo.db.users.update_one({
            'user_id': user.user_id
        }, {
            '$set': {
                'password': user.password
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
        return s.dumps({'reset_uid': self.user_id, 'new_email': new_email}).decode('ascii')

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
        if data.get('reset_uid') != self.user_id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if mongo.db.users.find_one({'email': new_email}):
            return False  # 邮箱已存在
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        mongo.db.users.update_one({
            'user_id': self.user_id
        }, {
            '$set': {
                'avatar_hash': self.avatar_hash
            }
        })
        return True

    def generate_access_token(self, expiration=3600):
        """
        生成用于 API 访问的Access_token
        :param expiration: Access_token 过期时间
        :return: 包含Access_token的字典
        """
        s1 = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        s2 = Serializer(current_app.config['SECRET_KEY'], expires_in=3600*24*10)
        access_token = s1.dumps({'token_uid': self.user_id, 'token_usage': 'access'}).decode('ascii')
        refresh_token = s2.dumps({'token_uid': self.user_id, 'token_usage': 'refresh'}).decode('ascii')
        return dict(access_token=access_token, refresh_token=refresh_token, expires_in=expiration,
                    expires_at=int(time.time())+expiration, token_type='Bearer')

    @staticmethod
    def verify_access_token(access_token):
        """
        验证 Access_token
        :param access_token: access_token
        :return: 验证成功返回对应用户,否则返回 False
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(access_token)
        except:
            return False
        if data.get('token_usage') != 'access':
            return False
        user = User(user_id=data.get('token_uid'))
        if not user or not user.user_id or not user.is_active:
            return False
        return user

    @staticmethod
    def refresh_access_token(refresh_token, expiration=3600):
        """
        刷新 Access_token
        :param refresh_token: refresh_token
        :param expiration: 新 Access_token 有效时间
        :return: 成功返回包含新的 Access_token 的字典,否则返回False
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(refresh_token)
        except:
            return False
        if data.get('token_usage') != 'refresh':
            return False
        if not data.get('token_uid'):
            return False
        sa = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        access_token = sa.dumps({'token_uid': data.get('token_uid'), 'token_usage': 'access'}).decode('ascii')
        return dict(access_token=access_token, refresh_token=refresh_token, expires_in=expiration,
                    expires_at=int(time.time())+expiration, token_type='Bearer')

    ##
    # 用户属性
    ##
    @property
    def is_active(self):
        """
        用户账户状态
        :return: 封禁用户返回 False,否则返回 True
        """
        status = self.status == 'active'
        return status

    def can(self, permission):
        """
        判断用户是否拥有对应权限
        :param permission: 权限
        :return: 拥有对应权限返回 True,否则返回False
        """
        return Role(role_id=self.role_id).can(permission)

    @property
    def is_administrator(self):
        """
        判断用户是否管理员(网站拥有者也是管理员)
        :return: 是则返回 True,否则返回 False
        """
        return (self.role_id == 1 or self.role_id == 2) and self.status == 'active'

    @property
    def is_editor(self):
        """
        判断用户是否编辑(广义的,更高权限的也符合)
        :return: 是则返回 True,否则返回 False
        """
        return (self.role_id in [1, 2, 3]) and self.status == 'active'

    @property
    def is_author(self):
        """
        判断用户是否作者(广义的,更高权限的也符合)
        :return: 是则返回 True,否则返回 False
        """
        return (self.role_id in [1, 2, 3, 4]) and self.status == 'active'

    @property
    def is_logged_in(self):
        """
        返回用户登录状态
        :return: 已登录返回 True,否则返回 False
        """
        return self.is_authenticated

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

    def get_role(self):
        """
        获取用户的 Role 模型
        :return: Role 模型
        """
        role = Role(role_id=self.role_id)
        if role and role.role_id:
            return role
        return None

    def get_user_posts(self, count=False, limit=10, offset=0):
        """
        获取用户的文章或者文章数量
        :param count: 是否返回文章数量
        :param limit: 最多返回文章数
        :param offset: 偏移量
        :return: 文章或者文章数量
        """
        filters = dict(author_id=self.user_id, status='published')
        if count:
            user_posts_count = Post.get_posts_count(filters)
            return user_posts_count
        posts = Post.get_posts(filters, limit=limit, offset=offset)
        return posts

    def get_user_comments(self, count=False, limit=20, offset=0):
        """
        获取用户的评论或者评论数量
        :param count: 是否返回评论数量
        :param limit: 最多返回评论数
        :param offset: 偏移量
        :return: 评论或者评论数量
        """
        filters = dict(user_id=self.user_id, approved=1)
        if count:
            user_comments_count = Comment.get_comments_count(filters)
            return user_comments_count
        comments = Comment.get_comments(filters, offset=offset, limit=limit, order_by='comment_id')
        return comments

    def update_user_login_time(self):
        """
        更新用户登录时间
        :return: 成功返回 True,否则返回 False
        """
        self.last_login = int(time.time())
        try:
            result = mongo.db.users.update_one({
                'user_id': self.user_id
            }, {
                '$set': {
                    'last_login': self.last_login
                }
            })
            if result.modified_count > 0:
                return True
            return False
        except:
            return False

    ##
    # 用户查询
    ##
    @staticmethod
    def get_user_by_field(field, value):
        """
        通过字段值获取用户实例
        :param field: 用户数据库字段(id/user_id/email/name)
        :param value: 字段值
        :return: 用户实例 or None
        """
        valid_fields = ['id', 'user_id', 'name', 'email']
        if field not in valid_fields:
            return None
        if field == 'id':
            field = 'user_id'
            # value = ObjectId(value)
        user = User(**{field: value})
        if user.user_id:
            return user
        return None

    @staticmethod
    def get_user_by_id(user_id):
        """
        通过用户 id 查询用户
        :param user_id: 用户 id,字符串类型
        :return: 用户实例 or None
        """
        return User.get_user_by_field('user_id', user_id)

    @staticmethod
    def get_user_by_email(email):
        """
        通过用户 email 查询用户
        :param email: 用户 email
        :return: 用户实例 or None
        """
        return User.get_user_by_field('email', email)

    @staticmethod
    def get_user_by_name(name):
        """
        通过用户名查询用户
        :param name: 用户名
        :return: 用户实例 or None
        """
        return User.get_user_by_field('name', name)

    ##
    # 用户管理
    ##
    @staticmethod
    def add_user(**kwargs):
        """
        增加新用户操作
        :param kwargs: 用户字段键值对
        :return: 添加成功返回 True,否则返回 False
        """
        if 'name' not in kwargs or 'email' not in kwargs or 'password' not in kwargs:
            return False  # 缺少必须字段
        user = mongo.db.users.find_one({'$or': [{'name': kwargs['name']}, {'email': kwargs['email']}]})
        if user:
            return False  # 邮箱或用户名被占用
        kwargs['user_id'] = get_next_sequence('user_id')
        if 'nickname' not in kwargs:
            kwargs['nickname'] = kwargs['name']  # 昵称为空则用用户名替代
        kwargs['password'] = generate_password_hash(str(kwargs['password']))
        if not mongo.db.users.find_one():
            kwargs['role_id'] = 1  # 首个用户为网站拥有者
        else:
            kwargs['role_id'] = 3  # 不允许接收注册表单传值,使用默认角色,要改变角色则由管理员以上等级用户更新用户属性
        kwargs['avatar_hash'] = hashlib.md5(kwargs['email'].encode('utf-8')).hexdigest()
        kwargs['status'] = 'active'
        kwargs['confirmed'] = 0
        kwargs['create_at'] = int(time.time())
        kwargs['update_at'] = int(time.time())

        try:
            result = mongo.db.users.insert_one(kwargs)
            return User(_id=result.inserted_id)
        except:
            return False

    @staticmethod
    def delete_user(user_id):
        """
        删除用户
        :param user_id: 用户 id 字符串
        :return: 删除成功返回 True,否则返回 False
        """
        try:
            # TODO 是否判断用户存在
            result = mongo.db.users.delete_one({'user_id': user_id})
            if result.deleted_count > 0:
                return True
            return False
        except:
            return False

    @staticmethod
    def ban_user(user_id):
        """
        封禁用户
        :param user_id: 用户 id 字符串
        :return: 封禁成功返回 True,否则返回 False
        """
        try:
            result = mongo.db.users.update_one({
                'user_id': user_id
            }, {
                '$set': {
                    'status': 'banned',
                    'update_at': int(time.time())
                }
            })
            if result.modified_count > 0:
                return True
            return False
        except:
            return False

    @staticmethod
    def cancel_ban_user(user_id):
        """
        解禁用户
        :param user_id: 用户 id 字符串
        :return: 解禁成功返回 True,否则返回 False
        """
        try:
            result = mongo.db.users.update_one({
                'user_id': user_id
            }, {
                '$set': {
                    'status': 'active',
                    'update_at': int(time.time())
                }
            })
            if result.modified_count > 0:
                return True
            return False
        except:
            return False

    def set_user_role(self, user_id, role):
        """
        设置用户角色 Administrator/Editor/Author, Owner不予提供,将在网站部署时自动分配给第一个注册用户,且数量限定1,该操作只能由等级
        更高的角色完成
        :param user_id: 用户 id 字符串
        :param role: 目标角色
        :return: 设置成功返回 True,否则返回 False
        """
        if (self.role_id != 1 and self.role_id != 2) or (self.role_id == 2 and role == 'Administrator'):
            return False  # 当前用户无权限变更用户角色
        role_id = Role.get_role_id(role)
        if not role_id:
            return False
        try:
            self.update_at = int(time.time())
            result = mongo.db.users.update_one({
                'user_id': user_id
            }, {
                '$set': {
                    'role_id': role_id,
                    'update_at': self.update_at
                }
            })
            if result.modified_count > 0:
                return True
            return False
        except:
            return False

    ##
    # 辅助
    #
    def get_homepage(self, external=False):
        """
        获取文章的固定链接
        :param external 是否显示完整链接
        :return: 文章固定链接
        """
        return url_for('main.user_homepage', user_id=self.user_id, _external=external)

    def __repr__(self):
        return '<User instance: %r>' % self.name


@login_manager.user_loader
def load_user(user_id):
    """
    加载用户
    :param user_id: 用户 id 字符串
    :return: 用户实例 or None
    """
    return User.get_user_by_id(int(user_id))


class AnonymousUser(AnonymousUserMixin):
    """
    匿名用户模型
    """

    def get_id(self):
        """
        覆盖UserMixin的同名方法,使之捕获正确字段作为用户 id
        :return:
        """
        return 0

    def can(self, permissions):
        """
        判断用户是否拥有对应权限
        :param permissions: 用户权限
        :return: 拥有对应权限返回 True,否则返回False
        """
        # TODO 待添加权限模型后更新
        pass

    @property
    def is_administrator(self):
        """
        判断用户是否管理员(网站拥有者也是管理员)
        :return: 是则返回 True,否则返回 False
        """
        return False

    @property
    def is_logged_in(self):
        """
        返回用户登录状态
        :return: 已登录返回 True,否则返回 False
        """
        return False

login_manager.anonymous_user = AnonymousUser