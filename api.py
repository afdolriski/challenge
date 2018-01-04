#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import Blueprint, render_template, request
from models import Client, User
from core import oauth

myapi = Blueprint('myApi', __name__)


@myapi.route('/oauth/token', methods=['POST'])
@oauth.token_handler
def access_token(*args, **kwargs):
    """ This endpoint is for exchanging/refreshing an access token.

    Returns a dictionary or None as the extra credentials for creating the
    token response.

    :param *args: Variable length argument list.
    :param **kwargs: Arbitrary keyword arguments.
    """
    return None


@myapi.route('/oauth/revoke', methods=['POST'])
@oauth.revoke_handler
def revoke_token():
    """ This endpoint allows a user to revoke their access token."""
    pass


@myapi.route('/', methods=['GET', 'POST'])
def management():
    """ This endpoint is for vieweing and adding users and clients. """
    if request.method == 'POST' and request.form['submit'] == 'Add User':
        # print(dict(request.form))
        # print(request.data)'
        User.save(**request.form)
    if request.method == 'POST' and request.form['submit'] == 'Add Client':
        Client.generate()
    return render_template('management.html', users=User.all(),
                           clients=Client.all())


@myapi.route('/test')
@oauth.require_oauth()
def my():
    """ This is an example endpoint we are trying to protect. """
    return "YOLO! Congratulations, you made it through and accessed the " \
        "protected resource!"

