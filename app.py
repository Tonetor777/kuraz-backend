from flask import Flask, jsonify, request
from flasgger import Swagger, swag_from
import json
import os

app = Flask(__name__)
swagger = Swagger(app)
DATA_FILE = 'tasks.json'


def read_tasks():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, 'r') as file:
        return json.load(file)


def write_tasks(tasks):
    with open(DATA_FILE, 'w') as file:
        json.dump(tasks, file, indent=2)


@app.route('/')
def home():
    return '<h1>✅ API is running</h1><p>Visit <a href="/apidocs">/apidocs</a> to test the api with Swagger UI.</p>'


@app.route('/api/tasks', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List of tasks',
            'examples': {
                'application/json': [
                    {'id': 1, 'title': 'Task', 'completed': False}
                ]
            }
        }
    }
})
def get_tasks():
    tasks = read_tasks()
    return jsonify(tasks), 200


@app.route('/api/tasks', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'}
                },
                'required': ['title']
            }
        }
    ],
    'responses': {
        201: {'description': 'Task is created successfully'},
        400: {'description': 'Invalid input'}
    }
})
def add_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Task title is required'}), 400

    tasks = read_tasks()
    new_task = {
        'id': len(tasks) + 1,
        'title': data['title'],
        'completed': False
    }
    tasks.append(new_task)
    write_tasks(tasks)
    return jsonify(new_task), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Enter the ID of the task to mark complete'
        }
    ],
    'responses': {
        200: {'description': 'Task is marked as completed'},
        404: {'description': 'Task is not found'}
    }
})
def complete_task(task_id):
    tasks = read_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = True
            write_tasks(tasks)
            return jsonify(task), 200
    return jsonify({'error': 'Task is not found'}), 404


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@swag_from({
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'Enter the ID of the task to delete'
        }
    ],
    'responses': {
        200: {'description': 'Task is deleted'},
        404: {'description': 'Task is not found'}
    }
})
def delete_task(task_id):
    tasks = read_tasks()
    new_tasks = [task for task in tasks if task['id'] != task_id]
    if len(tasks) == len(new_tasks):
        return jsonify({'error': 'Task is not found'}), 404
    write_tasks(new_tasks)
    return jsonify({'message': 'Task is deleted'}), 200


if __name__ == '__main__':
    app.run(debug=True)
