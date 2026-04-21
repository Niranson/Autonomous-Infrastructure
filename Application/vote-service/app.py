from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

votes = []

VOTER_SERVICE_URL = "http://voter-service:5000"

@app.route("/vote", methods=["POST"])
def cast_vote():
    data = request.json
    voter_id = data.get("voter_id")
    candidate_id = data.get("candidate_id")

    if not voter_id or not candidate_id:
        return jsonify({"error": "Invalid vote data"}), 400

    # 1️⃣ Check voter
    resp = requests.get(f"{VOTER_SERVICE_URL}/voters/{voter_id}")
    if resp.status_code != 200:
        return jsonify({"error": "Voter not found"}), 404

    voter = resp.json()
    if voter["has_voted"]:
        return jsonify({"error": "Voter already voted"}), 400

    # 2️⃣ Mark voter as voted
    mark = requests.put(f"{VOTER_SERVICE_URL}/voters/{voter_id}/vote")
    if mark.status_code != 200:
        return jsonify({"error": "Could not update voter"}), 500

    # 3️⃣ Save vote
    vote = {"voter_id": voter_id, "candidate_id": candidate_id}
    votes.append(vote)

    return jsonify({"message": "Vote cast successfully", "vote": vote}), 201

@app.route("/votes", methods=["GET"])
def get_votes():
    return jsonify(votes)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "vote-service running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
