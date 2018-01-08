from flask import Blueprint, request, abort

from flask_restful import Api, Resource, reqparse, fields, marshal_with

from core import oauth
import models

album_fields = {
    'userId': fields.Integer,
    'id': fields.Integer,
    'title': fields.String
}

parser = reqparse.RequestParser()
parser.add_argument(
    'title',
    required=True,
    help='No title provide.',
    location=['form', 'json']
)

def album_or_404(id):
    album = models.Album.query.get(id)
    return album if album else abort(404)

def is_allowed(user_id, album_user_id):
    return True if user_id == album_user_id else abort(401)

class AlbumList(Resource):

    @marshal_with(album_fields)
    def get(self):
        if request.args:
            user_id = request.args['userId']
            albums = models.Album.query.filter_by(userId=user_id).all()
        else:
            albums = models.Album.query.all()
        return albums

    @marshal_with(album_fields)
    @oauth.require_oauth()
    def post(self):
        user_id = request.oauth.user.id
        kwargs = parser.parse_args()
        album = models.Album.save(user_id, **kwargs)
        return album, 201

class Album(Resource):

    @marshal_with(album_fields)
    def get(self, id):
        return album_or_404(id)

    @marshal_with(album_fields)
    @oauth.require_oauth()
    def put(self, id):
        album = album_or_404(id)
        user_id = request.oauth.user.id
        if is_allowed(user_id, album.userId):
            kwargs = parser.parse_args()
            album = models.Album.update(id, **kwargs)
            return album

    @oauth.require_oauth()
    def delete(self, id):
        user_id = request.oauth.user.id
        album = album_or_404(id)
        if is_allowed(user_id, album.userId):
            models.Album.delete(album)
            return '', 204

albums_api = Blueprint('resources.albums', __name__)

api = Api(albums_api)

api.add_resource(
    AlbumList,
    '/albums',
    endpoint='albums'
)

api.add_resource(
    Album,
    '/albums/<int:id>'
)