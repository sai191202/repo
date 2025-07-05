from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# In-memory storage for webhook actions
actions = []

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json

    # Extract common details
    github_event = request.headers.get('X-GitHub-Event')

    if github_event == "push":
        doc = {
            "request_id": data["after"],
            "author": data["pusher"]["name"],
            "action": "PUSH",
            "from_branch": None,
            "to_branch": data["ref"].split("/")[-1],
            "timestamp": datetime.utcnow().isoformat()
        }

    elif github_event == "pull_request":
        pr = data["pull_request"]
        doc = {
            "request_id": str(pr["id"]),
            "author": pr["user"]["login"],
            "action": "PULL_REQUEST",
            "from_branch": pr["head"]["ref"],
            "to_branch": pr["base"]["ref"],
            "timestamp": pr["created_at"]
        }

    else:
        return jsonify({"message": "Unsupported event type"}), 400

    actions.append(doc)
    return jsonify({"message": "Webhook received"}), 200

if __name__ == '__main__':
    app.run(port=5000)