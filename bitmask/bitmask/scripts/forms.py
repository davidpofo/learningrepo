# -*- coding: utf-8 -*-

from wtforms import Form, StringField, PasswordField, validators


class LoginForm(Form):
    username = StringField('Username:', validators=[validators.required(), validators.Length(min=1, max=30)])
    password = PasswordField('Password:', validators=[validators.required(), validators.Length(min=1, max=30)])


class MPKForm(Form):
    title = StringField('Title:', validators=[validators.required(), validators.Length(min=1, max=30)])
    mpk = StringField('Master Pub:', validators=[validators.required(), validators.Length(min=30, max=255)])
