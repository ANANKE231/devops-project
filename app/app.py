from flask import Flask, request, jsonify, render_template_string
import datetime
import os

app = Flask(__name__)

# In-memory store for demo
messages = []

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DevOps Demo App</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Courier New', monospace; background: #0d0d0d; color: #e0e0e0; min-height: 100vh; padding: 40px 20px; }
    h1 { color: #00ff88; font-size: 2rem; margin-bottom: 8px; }
    .subtitle { color: #666; margin-bottom: 40px; font-size: 0.85rem; letter-spacing: 2px; text-transform: uppercase; }
    .card { background: #161616; border: 1px solid #2a2a2a; border-radius: 8px; padding: 24px; margin-bottom: 24px; max-width: 640px; }
    label { display: block; color: #888; font-size: 0.8rem; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
    input, textarea { width: 100%; background: #0d0d0d; border: 1px solid #333; color: #e0e0e0; padding: 10px 14px; border-radius: 4px; font-family: inherit; font-size: 0.95rem; margin-bottom: 16px; }
    input:focus, textarea:focus { outline: none; border-color: #00ff88; }
    button { background: #00ff88; color: #0d0d0d; border: none; padding: 10px 24px; border-radius: 4px; font-family: inherit; font-weight: bold; cursor: pointer; font-size: 0.9rem; letter-spacing: 1px; }
    button:hover { background: #00cc6a; }
    .msg { border-left: 3px solid #00ff88; padding: 10px 16px; margin-bottom: 12px; background: #111; border-radius: 0 4px 4px 0; }
    .msg .meta { font-size: 0.75rem; color: #555; margin-bottom: 4px; }
    .health { display: inline-block; width: 8px; height: 8px; background: #00ff88; border-radius: 50%; margin-right: 8px; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }
  </style>
</head>
<body>
  <h1>⬡ DevOps Demo App</h1>
  <p class="subtitle">CI/CD · IaC · Blue-Green Deploy</p>

  <div class="card">
    <label>Post a Message</label>
    <input type="text" id="author" placeholder="Your name" />
    <textarea id="body" rows="3" placeholder="Write something..."></textarea>
    <button onclick="postMsg()">Submit</button>
  </div>

  <div class="card">
    <label><span class="health"></span>Live Feed</label>
    <div id="feed">{% for m in messages %}<div class="msg"><div class="meta">{{ m.author }} · {{ m.timestamp }}</div>{{ m.body }}</div>{% endfor %}</div>
  </div>

  <script>
    async function postMsg() {
      const author = document.getElementById('author').value || 'Anonymous';
      const body = document.getElementById('body').value;
      if (!body.trim()) return;
      const res = await fetch('/api/messages', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({author, body})
      });
      const data = await res.json();
      document.getElementById('body').value = '';
      loadFeed();
    }
    async function loadFeed() {
      const res = await fetch('/api/messages');
      const data = await res.json();
      const feed = document.getElementById('feed');
      feed.innerHTML = data.messages.map(m =>
        `<div class="msg"><div class="meta">${m.author} · ${m.timestamp}</div>${m.body}</div>`
      ).join('');
    }
    setInterval(loadFeed, 5000);
  </script>
</body>
</html>"""


@app.route('/')
def index():
    return render_template_string(HTML, messages=messages)


@app.route('/health')
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": os.environ.get("APP_VERSION", "1.0.0"),
        "env": os.environ.get("APP_ENV", "production")
    })


@app.route('/api/messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": messages})


@app.route('/api/messages', methods=['POST'])
def post_message():
    data = request.get_json()
    if not data or not data.get('body'):
        return jsonify({"error": "body is required"}), 400
    msg = {
        "author": data.get("author", "Anonymous"),
        "body": data["body"],
        "timestamp": datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    }
    messages.append(msg)
    return jsonify({"status": "created", "message": msg}), 201


@app.route('/api/echo/<name>')
def echo(name):
    return jsonify({"echo": name, "timestamp": datetime.datetime.utcnow().isoformat()})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
