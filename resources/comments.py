from flask import Blueprint, abort, request

from flask_restful import reqparse, Api, Resource, fields, marshal_with

from core import oauth
import models

comment_fields = {
    'postId': fields.Integer,
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'body': fields.String
}

def comment_or_404(id):
    comment = models.Comment.query.get(id)
    return comment if comment else abort(404)

def is_allowed(user_email, comment_email):
    return True if user_email == comment_email else abort(401)

class CommentList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'postId',
            required=True,
            help='No post provided.',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'body',
            required=True,
            help='No body provided.',
            location=['form', 'json']
        )
        super(CommentList, self).__init__()

    @marshal_with(comment_fields)
    def get(self):
        if request.args:
            postId = request.args['postId']
            comments = models.Comment.query.filter_by(postId=postId).all()
        else:
            comments = models.Comment.query.all()
        return comments

    @marshal_with(comment_fields)
    @oauth.require_oauth()
    def post(self):
        kwargs = self.reqparse.parse_args()
        user = request.oauth.user
        kwargs['name'] = user.name
        kwargs['email'] = user.email
        comment = models.Comment.save(**kwargs)
        return comment, 201

class Comment(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'body',
            required=True,
            help='No body provided.',
            location=['form', 'json']
        )
        super(Comment, self).__init__()
    
    @marshal_with(comment_fields)
    def get(self, id):
        return comment_or_404(id)

    @marshal_with(comment_fields)
    @oauth.require_oauth()
    def put(self, id):
        comment = comment_or_404(id)
        kwargs = self.reqparse.parse_args()
        user_email = request.oauth.user.email
        if is_allowed(user_email, comment.email):
            comment = models.Comment.update(id, **kwargs)
            return comment

    @oauth.require_oauth()
    def delete(self, id):
        comment = comment_or_404(id)
        user_email = request.oauth.user.email
        if is_allowed(user_email, comment.email):
            models.Comment.delete(comment)
            return '', 204

comments_api = Blueprint('resources.comments', __name__)
api = Api(comments_api)
api.add_resource(
    CommentList,
    '/comments',
    endpoint='comments'
)

api.add_resource(
    Comment,
    '/comments/<int:id>'
)