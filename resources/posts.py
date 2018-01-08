from flask import jsonify, Blueprint, abort, request

from flask_restful import Resource, Api, reqparse, fields, marshal_with
            

from core import oauth
import models

post_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'userId': fields.Integer,
    'body': fields.String
}

comment_fields = {
    'postId': fields.Integer,
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'body': fields.String
}

def post_or_404(id):
    post = models.Post.query.filter_by(id=id).first()
    return post if post else abort(404)

def is_authorized(user_id, post_userId):
    return True if user_id == post_userId else abort(401)


class PostList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No title provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'body',
            required=True,
            help='No body provided',
            location=['form', 'json']
        )
        super(PostList, self).__init__()

    @marshal_with(post_fields)
    def get(self):
        if request.args:
            userId = request.args['userId']
            posts = models.Post.query.filter_by(userId=userId).all()
        else:
            posts = models.Post.query.all()
        return posts

    @marshal_with(post_fields)
    @oauth.require_oauth()
    def post(self):
        user_id = request.oauth.user.id
        kwargs = self.reqparse.parse_args()
        todo = models.Post.save(user_id, **kwargs)
        return todo, 201

class Post(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', location=['form', 'json'])
        self.reqparse.add_argument('body', location=['form', 'json'])
        super(Post, self).__init__()

    @marshal_with(post_fields)
    def get(self, id):
        return post_or_404(id)
    
    @marshal_with(post_fields)
    @oauth.require_oauth()
    def put(self, id):
        post = post_or_404(id)
        user_id = request.oauth.user.id
        if is_authorized(user_id, post.userId):
            kwargs = self.reqparse.parse_args()
            kwargs = dict((k, v) for k, v in kwargs.items() if v)
            post = models.Post.update(id, **kwargs)
            return post
        abort(500)

    @oauth.require_oauth()
    def delete(self, id):
        post = post_or_404(id)
        user_id = request.oauth.user.id
        if is_authorized(user_id, post.userId):
            result = models.Post.delete(post)
            return '', 204 if result else abort(500)

class PostComments(Resource):

    @marshal_with(comment_fields)
    def get(self, id):
        posts = models.Post.query.get(id).comments
        return posts


posts_api = Blueprint('resources.posts', __name__)

api = Api(posts_api)

api.add_resource(
    PostList,
    '/posts',
    endpoint='posts'
)
api.add_resource(
    Post,
    '/posts/<int:id>'
)
api.add_resource(
    PostComments,
    '/posts/<int:id>/comments'
)
