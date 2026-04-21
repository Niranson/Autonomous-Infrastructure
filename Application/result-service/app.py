from flask import Flask, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

VOTE_SERVICE_URL = "http://vote-service:5000"

@app.route("/results", methods=["GET"])
def get_results():
    
    response = requests.get(f"{VOTE_SERVICE_URL}/votes")

    if response.status_code != 200:
        return jsonify({"error": "Unable to fetch votes"}), 500

    votes = response.json()

    results = {}
    for vote in votes:
        cid = vote["candidate_id"]
        results[cid] = results.get(cid, 0) + 1

    return jsonify(results)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "result-service running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
