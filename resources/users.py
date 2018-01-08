import json

from flask import jsonify, Blueprint, abort, request
from sqlalchemy.exc import IntegrityError

from flask_restful import Resource, Api, reqparse, fields, marshal_with

from core import oauth
import models

user_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'name': fields.String,
    'email': fields.String,
    'address': {
        'geo': {
            'lat': fields.String,
            'lng': fields.String
        },
        'street': fields.String,
        'suite': fields.String,
        'city': fields.String,
        'zipcode': fields.String
    },
    'phone': fields.String,
    'website': fields.String,
    'company': {
        'name': fields.String(attribute='cmpName'),
        'catachPhrase': fields.String,
        'bs': fields.String
    }
}

def is_allowed(authenticated_id, user_id):
    return True if authenticated_id == user_id else abort(401)

parser = reqparse.RequestParser()
parser.add_argument('username',
    required=True,
    help='No username provided',
    location=['form', 'json']
)
parser.add_argument(
    'name',
    required=True,
    help='No name provided',
    location=['form', 'json']
)
parser.add_argument(
    'password',
    required=True,
    help='No password provided',
    location=['form', 'json']
)
parser.add_argument(
    'email',
    required=True,
    help='No email provided',
    location=['form', 'json']
)
parser.add_argument(
    'city',
    location=['form', 'json']
)
parser.add_argument(
    'zipcode',
    location=['form', 'json']
)
parser.add_argument(
    'suite',
    location=['form', 'json']
)
parser.add_argument(
    'street',
    location=['form', 'json']
)
parser.add_argument(
    'lat',
    location=['form', 'json']
)
parser.add_argument(
    'lng',
    location=['form', 'json']
)
parser.add_argument(
    'phone',
    location=['form', 'json']
)
parser.add_argument(
    'website',
    location=['form', 'json']
)
parser.add_argument(
    'cmpName',
    location=['form', 'json']
)
parser.add_argument(
    'catchPhrase',
    location=['form', 'json']
)
parser.add_argument(
    'bs',
    location=['form', 'json']
)

def user_or_404(id):
    user = models.User.query.get(id)
    if user == None:
        abort(404, 'User not found.')
    return user

class UserList(Resource):
    def __init__(self):
        self.reqparse = parser
        super(UserList, self).__init__()

    @marshal_with(user_fields)
    def get(self):
        users = models.User.all()
        return users

    @marshal_with(user_fields)
    def post(self):
        args = self.reqparse.parse_args()
        try:
            user = models.User.save(**args)
        except IntegrityError:
            abort(404, "Username already taken.")
        return user, 201

class User(Resource):
    def __init__(self):
        self.reqparse = parser
        self.reqparse.remove_argument('password')
        self.reqparse.replace_argument('username')
        self.reqparse.replace_argument('email')
        self.reqparse.replace_argument('website')
        self.reqparse.replace_argument('phone')
        self.reqparse.replace_argument('name')
        super(User, self).__init__()

    @marshal_with(user_fields)
    def get(self, id):
        return user_or_404(id)

    @oauth.require_oauth()
    @marshal_with(user_fields)
    def put(self, id):
        user_id = request.oauth.user.id
        user = user_or_404(id)
        if is_allowed(user_id, user.id):
            kwargs = self.reqparse.parse_args()
            kwargs = dict((k,v) for k,v in kwargs.iteritems() if v)
            user = models.User.update(id, **kwargs)
            return user
    
    @oauth.require_oauth()
    def delete(self, id):
        user = user_or_404(id)
        authenticated_user = request.oauth.user.id
        if is_allowed(authenticated_user, user.id):
            result = models.User.delete(user)
            return '', 204 if result else abort(500)

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