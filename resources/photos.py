from flask import Blueprint, abort, request

from flask_restful import Resource, Api, fields,reqparse, marshal_with

from core import oauth
import models

photo_fields = {
    'albumId': fields.Integer,
    'id': fields.Integer,
    'title': fields.String,
    'url': fields.String,
    'thumbnailUrl': fields.String
}

def photo_or_404(id):
    photo = models.Photo.query.get(id)
    return photo if photo else abort(404)

def is_allowed(user_id, photo_user_id):
    return True if user_id == photo_user_id else abort(401)

class PhotoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'albumId',
            required=True,
            help='No album specified',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No title specified',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'url',
            required=True,
            help='No url specified',
            location=['form', 'json']
        )
        super(PhotoList, self).__init__()

    @marshal_with(photo_fields)
    def get(self):
        if request.args:
            albumId = request.args['albumId']
            photos = models.Photo.query.filter_by(albumId=albumId).all()
        else:
            photos = models.Photo.query.all()
        return photos

    @marshal_with(photo_fields)
    @oauth.require_oauth()
    def post(self):
        kwargs = self.reqparse.parse_args()
        kwargs['thumbnailUrl'] = kwargs['url']
        photo = models.Photo.save(**kwargs)
        return photo, 201

class Photo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('albumId', location=['form', 'json'])
        self.reqparse.add_argument('title', location=['form', 'json'])
        self.reqparse.add_argument('url', location=['form', 'json'])
        self.reqparse.add_argument('thumbnailUrl', location=['form', 'json'])
        super(Photo, self).__init__()

    @marshal_with(photo_fields)
    def get(self, id):
        return photo_or_404(id)

    @marshal_with(photo_fields)
    @oauth.require_oauth()
    def put(self, id):
        photo = photo_or_404(id)
        user_id = request.oauth.user.id
        if is_allowed(user_id, photo.album.userId):
            kwargs = self.reqparse.parse_args()
            kwargs['thumbnailUrl'] = kwargs['url']
            kwargs = dict((k, v) for k, v in kwargs.items() if v)
            photo = models.Photo.update(id, **kwargs)
        return photo

    @oauth.require_oauth()
    def delete(self, id):
        photo = photo_or_404(id)
        user_id = request.oauth.user.id
        if is_allowed(user_id, photo.album.userId):
            models.Photo.delete(photo)
            return '', 204
        abort(500)

photos_api = Blueprint('resources.photo', __name__)
api = Api(photos_api)

api.add_resource(
    PhotoList,
    '/photos',
    endpoint='photos'
)

api.add_resource(
    Photo,
    '/photos/<int:id>'
)