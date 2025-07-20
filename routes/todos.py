from flask import  jsonify, request, Blueprint
from db import db
from models import Todo
from utils import token_required
from datetime import date

todos_bp = Blueprint("todos" , __name__)

@todos_bp.route('/' , methods=["GET"])
@token_required
def get_todos(user_id):
    todos = Todo.query.filter_by(user_id = user_id).all()
    results = []
    for todo in todos:
        results.append({
            'todo_id' : todo.id,
            'title' : todo.title,
            'status' : todo.status,
            'task_date' : todo.task_date.isoformat()
        })

    return jsonify(results)

@todos_bp.route('/add' , methods=["POST"])
@token_required
def add_todo(user_id):
    data = request.get_json()
    title = data.get('title')
    task_date = data.get('task_date' , date.today().isoformat())

    new_todo = Todo(
        title = title,
        status=False,
        task_date = date.fromisoformat(task_date),
        user_id = user_id
    )

    db.session.add(new_todo)
    db.session.commit()

    todos = Todo.query.filter_by(user_id = user_id).all()
    results = []
    for todo in todos :
        results.append({
            'todo_id' : todo.id,
            'title' : todo.title,
            'status' : todo.status,
            'task_date' : todo.task_date.isoformat()
        })

    return jsonify({'message' : 'Todo added', 'results' : results }),201

@todos_bp.route('/<int:todo_id>' , methods=['PUT'])
@token_required
def update_todo(todo_id , user_id):
    data = request.get_json()
    todo = Todo.query.filter_by(id = todo_id, user_id = user_id).first()

    if not todo:
        return jsonify({'message': 'Todo not found'}), 404

    todo.title = data.get('title' , todo.title)
    todo.status = data.get('status' , todo.status)
    db.session.commit()

    todos = Todo.query.filter_by(user_id = user_id).all()
    results = []

    for todo in todos:
        results.append({
            'todo_id': todo.id,
            'title': todo.title,
            'status': todo.status,
            'task_date': todo.task_date.isoformat()
        })

    return jsonify({'message': 'Todo updated' , 'results' : results}),201

@todos_bp.route('/<int:todo_id>' , methods=['DELETE'])
@token_required
def delete_todo(user_id , todo_id):
    todo = Todo.query.filter_by(id= todo_id , user_id = user_id).first()

    if not todo:
        return jsonify({'message': 'Todo not found'}),404

    db.session.delete(todo)
    db.session.commit()

    todos = Todo.query.filter_by(user_id = user_id).all()
    results = []

    for todo in todos:
        results.append({
            'todo_id': todo.id,
            'title': todo.title,
            'status': todo.status,
            'task_date': todo.task_date.isoformat()
        })

    return jsonify({'message': 'Todo deleted' , 'results' : results}), 201




