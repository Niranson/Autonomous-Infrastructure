from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

candidates = [
    {"id": 1, "name": "Candidate A", "party": "Party X"},
    {"id": 2, "name": "Candidate B", "party": "Party Y"},
    {"id": 3, "name": "Candidate C", "party": "Party Z"}
]

@app.route("/candidates", methods=["GET"])
def get_candidates():
    return jsonify(candidates)

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "candidate-service running"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
