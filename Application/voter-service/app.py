from flask import Flask, jsonify, request
from flask_cors import CORS

app=Flask(__name__)
CORS(app)

voters=[
    {"id":1, "name":"niran", "has_voted":False},
    {"id":2, "name":"durai", "has_voted":False},
    {"id":3, "name":"akash", "has_voted":False}
]

@app.route("/voters", methods=["GET"])
def get_voters():
    return jsonify(voters)

@app.route("/voters/<int:voter_id>", methods=["GET"])
def get_voter(voter_id):
    for voter in voters:
        if voter["id"]==voter_id:
            return jsonify(voter)
    
    return jsonify({"error": "Voter not found"}), 404


@app.route("/voters/<int:voter_id>/vote", methods=["PUT"])
def mark_voted(voter_id):
    for v in voters:
        if v["id"] == voter_id:
            if v["has_voted"]:
                return jsonify({"error": "Voter already voted"}), 400
            v["has_voted"] = True
            return jsonify({"message": "Voter marked as voted"})
    return jsonify({"error": "Voter not found"}), 404


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "voter-service running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
            