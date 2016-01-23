# coding=utf-8


from . import auth


@auth.route('/login.do')
def login_view():
    return '<h1>Login Page</h1>'
