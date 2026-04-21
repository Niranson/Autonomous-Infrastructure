from flask import Flask, request, Response
from flask_cors import CORS
import requests

app = Flask(__name__)

# 🔥 Enable CORS (VERY IMPORTANT)
CORS(app)

# -------------------------------
# 🔁 API GATEWAY ROUTES
# -------------------------------

# Candidate Service
@app.route("/candidate/<path:path>", methods=["GET"])
def candidate(path):
    res = requests.get(f"http://candidate-service:5000/{path}")
    return Response(res.content, status=res.status_code, content_type=res.headers.get("Content-Type"))

# Voter Service
@app.route("/voter/<path:path>", methods=["GET"])
def voter(path):
    res = requests.get(f"http://voter-service:5000/{path}")
    return Response(res.content, status=res.status_code, content_type=res.headers.get("Content-Type"))

# Vote Service
@app.route("/vote/<path:path>", methods=["POST"])
def vote(path):
    res = requests.post(
        f"http://vote-service:5000/{path}",
        json=request.json
    )
    return Response(res.content, status=res.status_code, content_type=res.headers.get("Content-Type"))

# Result Service
@app.route("/result/<path:path>", methods=["GET"])
def result(path):
    res = requests.get(f"http://result-service:5000/{path}")
    return Response(res.content, status=res.status_code, content_type=res.headers.get("Content-Type"))

# -------------------------------
# ❤️ HEALTH CHECK
# -------------------------------
@app.route("/health")
def health():
    return {"status": "gateway running"}

# -------------------------------
# 🚀 RUN APP
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
