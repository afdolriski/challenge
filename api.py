#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request
from models import Client, User
from core import oauth

myapi = Blueprint('myApi', __name__)

@myapi.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token(*args, **kwargs):
    return None

@oauth.usergetter
def get_user(username, password, *args, **kwargs):
    user = User.query.filter_by(username=username).first()
    if user.check_password(password):
        return user
    return None

@myapi.route('/oauth/revoke', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    pass

@myapi.route('/', methods=['GET', 'POST'])
def management():
    if request.method == 'POST' and request.form['submit'] == 'Add Client':
        Client.generate()
    return render_template('management.html', clients=Client.all())

@myapi.route('/test')
@oauth.require_oauth()
def my():
    return "YOLO! Congratulations, you made it through and accessed the " \
        "protected resource!"

