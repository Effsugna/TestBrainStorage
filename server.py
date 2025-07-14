
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, 'memory')

@app.route('/read', methods=['GET'])
def read_file():
    path = request.args.get('path')
    if not path:
        return jsonify({'error': 'No path specified'}), 400
    full_path = os.path.join(BASE_DIR, path)
    if not os.path.isfile(full_path):
        return jsonify({'error': 'File not found'}), 404
    with open(full_path, 'r') as f:
        content = f.read()
    return jsonify({'content': content})

@app.route('/write', methods=['POST'])
def write_file():
    data = request.json
    path = data.get('path')
    content = data.get('content')
    if not path or content is None:
        return jsonify({'error': 'Missing path or content'}), 400
    full_path = os.path.join(BASE_DIR, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, 'w') as f:
        f.write(content)
    return jsonify({'status': 'success', 'path': path})

@app.route('/list', methods=['GET'])
def list_files():
    files = []
    for root, dirs, filenames in os.walk(MEMORY_DIR):
        for name in filenames:
            rel_dir = os.path.relpath(root, BASE_DIR)
            files.append(os.path.join(rel_dir, name))
    return jsonify({'files': files})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

