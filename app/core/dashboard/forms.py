# coding=utf-8

from flask.ext.wtf import Form
from wtforms import StringField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.validators import DataRequired
from wtforms.validators import Email
from wtforms.validators import EqualTo
from wtforms.validators import Length


# class FindPassForm(Form):
#     """ 找回密码表单, 提供 Email 输入"""
#     email = StringField('Email', validators=[DataRequired(message=u'字段值不可为空'), Email(message=u'无效的邮件格式')])
#     submit = SubmitField('Submit')
#
#
# class ResetPassForm(Form):
#     """ 重设密码表单, 提供密码输入 """
#     password = PasswordField('Password', validators=[DataRequired(message=u'字段值不可为空'),
#                                                      Length(6, message=u'密码至少6位字符')])
#     password2 = PasswordField('Repeat password', validators=[DataRequired(message=u'字段值不可为空'),
#                                                              Length(6, message=u'密码至少6位字符'),
#                                                              EqualTo('password', message=u'两次输入的密码必须一致')])
#     submit = SubmitField('Submit')


class EditTopNaviForm(Form):
    """ 编辑导航菜单表单 """
    submit = SubmitField('Submit')