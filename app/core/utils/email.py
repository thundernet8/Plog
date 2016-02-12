# coding=utf-8

from threading import Thread

from flask import current_app
from flask import render_template
from flask.ext.mail import Message

from app import mail


def send_async_email(app, message):
    """
    异步发送邮件消息
    :param app: 当前 flask 应用
    :param message: 邮件消息
    :return:
    """
    with app.app_context():
        mail.send(message)


def send_mail(to, subject, template, **kwargs):
    """
    发送邮件
    :param to: 收件人
    :param subject: 主题
    :param template: 邮件模板
    :param kwargs: 其他参数
    :return:
    """
    app = current_app._get_current_object()
    message = Message(app.config['MAIL_SUBJECT_PREFIX'] + '' + subject, sender=app.config['MAIL_SENDER'],
                      recipients=[to])
    message.body = render_template(template + '.txt', **kwargs)
    message.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, message])
    thr.start()
    return thr
