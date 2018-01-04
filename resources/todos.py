from flask import jsonify, Blueprint, abort

from flask_restful import (Resource, Api, reqparse, inputs, fields, marshal, marshal_with, url_for)

import models

todo_fields = {
    'id': fields.Integer,
    'title': fields.String,
    'userId': fields.String,
    'completed': fields.Boolean
}

def todo_or_404(todo_id):
    try:
        todo = models.Todo.get(models.Todo.id==todo_id)
    except models.Todo.DoesNotExist:
        abort(404, 'Todo not found')
    else:
        return todo

class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No title provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'userId',
            required=True,
            help='No user id provided',
            location=['form', 'json']
        )
        super(TodoList, self).__init__()

    def get(self):
        todos = [marshal(todo, todo_fields) for todo in models.Todo.query.all()]
        return todos

    def post(self):
        args = self.reqparse.parse_args()
        todo = models.Todo.create(**args)
        return marshal(todo, todo_fields), 201

class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'title',
            required=True,
            help='No title provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'userId',
            required=True,
            help='No user id provided',
            location=['form', 'json']
        )
        self.reqparse.add_argument(
            'completed'
        )
        super(Todo, self).__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        return todo_or_404(id)

todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/todos/<int:id>',
    endpoint='todo'
)
