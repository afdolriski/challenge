from flask import jsonify, Blueprint, abort, request

from flask_restful import Resource, Api, reqparse, fields, marshal_with

from core import oauth
import models

todo_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'userId': fields.Integer,
    'completed': fields.Boolean
}

def todo_or_404(id):
    todo = models.Todo.query.get(id)
    return todo if todo else abort(404)

def is_allowed(user_id, todo_user_id):
    return True if user_id == todo_user_id else abort(401)

class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No title provided',
            location=['form', 'json']
        )
        super(TodoList, self).__init__()

    @marshal_with(todo_fields)
    def get(self):
        if request.args:
            userId = request.args['userId']
            todos = models.Todo.query.filter_by(userId=userId).all()
        else:
            todos = models.Todo.query.all()
        return todos

    @marshal_with(todo_fields)
    @oauth.require_oauth()
    def post(self):
        user_id = request.oauth.user.id
        args = self.reqparse.parse_args()
        todo = models.Todo.save(user_id, **args)
        return todo, 201

class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'completed'
        )
        super(Todo, self).__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        return todo_or_404(id)

    @marshal_with(todo_fields)
    @oauth.require_oauth()
    def put(self, id):
        todo = todo_or_404(id)
        user_id = request.oauth.user.id
        if is_allowed(user_id, todo.userId):
            kwargs = self.reqparse.parse_args()
            kwargs = dict((k, v) for k,v in kwargs.items() if v)
            todo = models.Todo.update(id, **kwargs)
            return todo

    @oauth.require_oauth()
    def delete(self, id):
        todo = todo_or_404(id)
        user_id = request.oauth.user.id
        if is_allowed(user_id, todo.userId):
            result = models.Todo.delete(todo)
            return '', 204 if result else abort(500)


todos_api = Blueprint('resources.todos', __name__)

api = Api(todos_api)

api.add_resource(
    TodoList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/todos/<int:id>'
)
