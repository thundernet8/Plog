# coding=utf-8

from flask import jsonify

from . import api


@api.route('/register', methods=['POST'])
def register():
    """
    注册 api 接口
    :return:
    """
