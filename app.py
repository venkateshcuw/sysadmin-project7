import os
import requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://ollama:11434")
MODEL_NAME = os.environ.get("MODEL_NAME", "llama3.2:3b")

SYSTEM_PROMPT = (
    "You are Verse Helper, a friendly assistant for Mercy Lutheran that helps "
    "students find, understand, and reflect on Bible verses. Keep answers "
    "short, kind, and age-appropriate."
)

INDEX_HTML = """
<!doctype html>
<html>
<head><title>Verse Helper</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 40px auto;">
  <h2>Verse Helper</h2>
  <textarea id="q" rows="3" style="width:100%" placeholder="Ask about a verse..."></textarea><br><br>
  <button onclick="ask()">Ask</button>
  <pre id="a" style="white-space: pre-wrap; background:#f4f4f4; padding:10px;"></pre>
  <script>
    async function ask() {
      const q = document.getElementById('q').value;
      document.getElementById('a').textContent = 'Thinking...';
      const res = await fetch('/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({question: q})
      });
      const data = await res.json();
      document.getElementById('a').textContent = data.answer || JSON.stringify(data);
    }
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    return Response(INDEX_HTML, mimetype="text/html")


@app.route("/health")
def health():
    return jsonify(status="ok"), 200


@app.route("/ask", methods=["POST"])
def ask():
    body = request.get_json(force=True, silent=True) or {}
    question = body.get("question", "").strip()
    if not question:
        return jsonify(error="question is required"), 400

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        "stream": False,
    }

    try:
        resp = requests.post(
            f"{OLLAMA_URL}/v1/chat/completions", json=payload, timeout=60
        )
        resp.raise_for_status()
        data = resp.json()
        answer = data["choices"][0]["message"]["content"]
        return jsonify(answer=answer), 200
    except Exception as exc:
        return jsonify(error=str(exc)), 502


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
