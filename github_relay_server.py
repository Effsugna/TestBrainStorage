
from flask import Flask, request, jsonify
import requests
import subprocess
import os
from base64 import b64encode

app = Flask(__name__)

# Load GitHub token from environment variable or insert here temporarily
GITHUB_TOKEN = os.environ.get("GITHUB_PAT") or "INSERT_YOUR_GITHUB_PAT_HERE"
REPO_OWNER = "Effsugna"
REPO_NAME = "TestBrainStorage"

@app.route("/push-to-github", methods=["POST"])
def push_to_github():
    data = request.json
    path = data.get("path")
    content = data.get("content")
    message = data.get("message")

    if not path or content is None or not message:
        return jsonify({"error": "Missing path, content, or message"}), 400

    # Prepare GitHub API URL and content
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{path}"
    encoded_content = b64encode(content.encode()).decode()

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    payload = {
        "message": message,
        "content": encoded_content,
        "branch": "main"
    }

    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 201:
        return jsonify({"status": "success", "path": path})
    else:
        return jsonify({"error": response.json()}), response.status_code

@app.route('/write', methods=['POST'])
def write_file():
    data = request.get_json()
    path = data.get('path')
    content = data.get('content')

    if not path or content is None:
        return jsonify({"error": "Missing path or content"}), 400

    try:
        # Ensure target directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Write file
        with open(path, 'w') as f:
            f.write(content)

        # Git add/commit/push from repo root
        repo_root = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(["git", "add", path], cwd=repo_root)
        subprocess.run(["git", "commit", "-m", f"Add {path} via ngrok relay"], cwd=repo_root)
        subprocess.run(["git", "push"], cwd=repo_root)

        return jsonify({"path": path, "status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5050)
