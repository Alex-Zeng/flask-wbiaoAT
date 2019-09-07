from flask import Flask
from flask_restful import Api, Resource, reqparse, abort ,fields, marshal_with
import werkzeug
import time

app = Flask(__name__)
api = Api(app)

TODOS = {
    'todo1': {'task': 'build an API'},
    'todo2': {'task': '?????'},
    'todo3': {'task': 'profit!','namelist': 'todoname','address': 'addresssdd'},

}


def abort_if_todo_doesnt_exist(todo_id):
    if todo_id not in TODOS:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


parser = reqparse.RequestParser()
# 必需的参数:要求一个值传递的参数，只需要添加 required=True 来调用 add_argument()
parser.add_argument('task', type=str, required=True, help="task cannot be blank!")
# 如果你要接受一个键有多个值的话，你可以传入 action='append'
parser.add_argument('name', type=str, action='append')
# 别名 dest=xx   parser.parse_args()['xx']
parser.add_argument('argssss', type=str, dest='public_args')

# 参数来源 form args headers cookies files
# Look only in the POST body
parser.add_argument('name', type=int, location='form')

# Look only in the querystring
parser.add_argument('PageSize', type=int, location='args')

# From the request headers
parser.add_argument('User-Agent', type=str, location='headers')

# From http cookies
parser.add_argument('session_id', type=str, location='cookies')

# From file uploads
# parser.add_argument('picture', type=werkzeug.datastructures.FileStorage, location='files')
# 多个位置
parser.add_argument('text', location=['headers', 'values'])


resource_fields = {
    'namelist': fields.String,
    # 重命名属性
    '其实我是address': fields.String(attribute='address'),
    # 默认值default
    'date_updated': fields.DateTime(default=time.asctime()),
    'https_uri': fields.Url(endpoint='todolist', absolute=True )
}
class Todo(Resource):

    @marshal_with(resource_fields, envelope='resource')
    def get(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        return TODOS[todo_id]

    def delete(self, todo_id):
        abort_if_todo_doesnt_exist(todo_id)
        del TODOS[todo_id]
        return '', 204

    def put(self, todo_id):
        args = parser.parse_args()
        task = {'task': args['task']}
        name = {'name': args['name']}
        print(name)
        TODOS[todo_id] = task
        return task, 201


# TodoList
#   shows a list of all todos, and lets you POST to add new tasks
class TodoList(Resource):
    def get(self):
        return TODOS

    def post(self):
        args = parser.parse_args()
        todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        todo_id = 'todo%i' % todo_id
        TODOS[todo_id] = {'task': args['task']}
        return TODOS[todo_id], 201


##
## Actually setup the Api resource routing here
##
api.add_resource(TodoList, '/todos')
api.add_resource(Todo, '/todos/<todo_id>')

if __name__ == '__main__':
    app.run(debug=True)
