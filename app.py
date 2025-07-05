from flask import Flask, request, jsonify
from datetime import datetime
from pymongo import MongoClient
import os

app = Flask(__name__)


client = MongoClient(os.getenv('mongodb+srv://pellurusai22:pellurusai22@cluster0.iwpdndh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', 'mongodb://localhost:27017/'))
db = client['webhook_db']
actions_collection = db['actions']



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

    
    actions_collection.insert_one(doc)
    return jsonify({"message": "Webhook received"}), 200


@app.route('/logs', methods=['GET'])
def get_logs():
    logs = list(actions_collection.find({}, {"_id": 0}))
    return jsonify(logs)

if __name__ == '__main__':
    app.run(port=5000)
