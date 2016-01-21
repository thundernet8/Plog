# coding=utf-8

from flask import send_file

from . import main


@main.route('/favicon.ico')
def favicon():
    """
    收藏夹栏图标
    :return:
    """
    return send_file('static/dist/styles/img/favicon.ico', as_attachment=False)


@main.route('/')
def index_home():
    return 'Hello, plog'
