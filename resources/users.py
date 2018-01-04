import json

from flask import jsonify, Blueprint, abort, make_response

from flask_restful import (Resource, Api, reqparse, inputs, fields, 
                            url_for, marshal, marshal_with)

import models

user_fields = {
    'username': fields.String,
    'name': fields.String,
    'email': fields.String,
    'city': fields.String,
    'cmpName': fields.String,
    'phone': fields.String,
    'company': fields.String
}

def user_or_404(user_id):
    try:
        user = models.User.get(models.User.id==user_id)
    except models.User.DoesNotExist:
        abort(404, 'User not found')
    else:
        return user

class UserList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'username',
            # required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'email',
            required=True,
            help='No email provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'city',
            required=True,
            help='No address provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'phone',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'password',
            required=True,
            help='No password provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'website',
            required=True,
            help='No website provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'cmpName',
            required=True,
            help='No username provided',
            location=['form', 'json']
        )
        super(UserList, self).__init__()

    def get(self):
        users = [marshal(user, user_fields) for user in models.User.query.all()]
        return users

    def post(self):
        args = self.reqparse.parse_args()
        user = models.User.save(**args)
        print(user)
        return marshal(user, user_fields), 201

class User(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        super(User, self).__init__()

    @marshal_with(user_fields)
    def get(self, id):
        return user_or_404(id)


users_api = Blueprint('resources.users', __name__)
api = Api(users_api)
api.add_resource(
    UserList,
    '/users',
    endpoint='users'
)

api.add_resource(
    User,
    '/users/<int:id>'
)