from flask import Flask, request, jsonify, render_template_string
import datetime
import os

app = Flask(__name__)

messages = []

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DevOps Demo</title>
  <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;700;800&display=swap" rel="stylesheet">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg: #080b10;
      --surface: #0e1218;
      --surface2: #141920;
      --border: rgba(255,255,255,0.07);
      --border-bright: rgba(99,210,143,0.3);
      --green: #63d28f;
      --green-dim: #2a6645;
      --amber: #f0b429;
      --red: #f56565;
      --text: #e2e8f0;
      --text-dim: #64748b;
      --text-muted: #334155;
      --mono: 'DM Mono', monospace;
      --sans: 'Syne', sans-serif;
    }

    html { scroll-behavior: smooth; }

    body {
      font-family: var(--mono);
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.6;
      overflow-x: hidden;
    }

    /* ── Grid background ── */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(rgba(99,210,143,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(99,210,143,0.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
      z-index: 0;
    }

    /* ── Glow orb ── */
    body::after {
      content: '';
      position: fixed;
      top: -200px;
      left: 50%;
      transform: translateX(-50%);
      width: 600px;
      height: 600px;
      background: radial-gradient(circle, rgba(99,210,143,0.06) 0%, transparent 70%);
      pointer-events: none;
      z-index: 0;
    }

    .wrapper {
      position: relative;
      z-index: 1;
      max-width: 860px;
      margin: 0 auto;
      padding: 48px 24px 80px;
    }

    /* ── Header ── */
    header {
      margin-bottom: 52px;
      animation: fadeDown 0.6s ease both;
    }

    .header-top {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 12px;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .logo-icon {
      width: 36px;
      height: 36px;
      border: 1.5px solid var(--green);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
      color: var(--green);
      box-shadow: 0 0 16px rgba(99,210,143,0.2);
    }

    h1 {
      font-family: var(--sans);
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text);
      letter-spacing: -0.02em;
    }

    .status-bar {
      display: flex;
      align-items: center;
      gap: 20px;
    }

    .badge {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.7rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--text-dim);
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 4px 10px;
      border-radius: 4px;
    }

    .dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--green);
      box-shadow: 0 0 6px var(--green);
      animation: pulse 2.4s ease-in-out infinite;
    }

    .dot.amber { background: var(--amber); box-shadow: 0 0 6px var(--amber); }

    .tagline {
      font-size: 0.75rem;
      color: var(--text-muted);
      letter-spacing: 0.15em;
      text-transform: uppercase;
    }

    /* ── Stats row ── */
    .stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      margin-bottom: 32px;
      animation: fadeUp 0.6s 0.1s ease both;
    }

    .stat {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 16px 20px;
      transition: border-color 0.2s;
    }

    .stat:hover { border-color: var(--border-bright); }

    .stat-label {
      font-size: 0.65rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 6px;
    }

    .stat-value {
      font-family: var(--sans);
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--green);
    }

    .stat-value.neutral { color: var(--text); }

    /* ── Main grid ── */
    .grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
      margin-bottom: 16px;
      animation: fadeUp 0.6s 0.2s ease both;
    }

    /* ── Cards ── */
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      transition: border-color 0.2s, box-shadow 0.2s;
    }

    .card:hover { border-color: var(--border-bright); }

    .card-full {
      grid-column: 1 / -1;
      animation: fadeUp 0.6s 0.3s ease both;
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 20px;
    }

    .card-title {
      font-size: 0.7rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-dim);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .card-title::before {
      content: '';
      display: inline-block;
      width: 3px;
      height: 12px;
      background: var(--green);
      border-radius: 2px;
    }

    /* ── Form ── */
    .field { margin-bottom: 14px; }

    label {
      display: block;
      font-size: 0.65rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: var(--text-muted);
      margin-bottom: 6px;
    }

    input, textarea {
      width: 100%;
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 10px 14px;
      border-radius: 7px;
      font-family: var(--mono);
      font-size: 0.85rem;
      transition: border-color 0.2s, box-shadow 0.2s;
      resize: none;
      outline: none;
    }

    input::placeholder, textarea::placeholder { color: var(--text-muted); }

    input:focus, textarea:focus {
      border-color: var(--green-dim);
      box-shadow: 0 0 0 3px rgba(99,210,143,0.08);
    }

    textarea { height: 80px; }

    .btn {
      width: 100%;
      background: var(--green);
      color: #050905;
      border: none;
      padding: 11px 20px;
      border-radius: 7px;
      font-family: var(--sans);
      font-weight: 700;
      font-size: 0.8rem;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      cursor: pointer;
      transition: background 0.15s, transform 0.1s, box-shadow 0.2s;
      position: relative;
      overflow: hidden;
    }

    .btn:hover {
      background: #7de0a3;
      box-shadow: 0 0 20px rgba(99,210,143,0.3);
    }

    .btn:active { transform: scale(0.98); }

    .btn.loading { opacity: 0.6; pointer-events: none; }

    /* ── Endpoints ── */
    .endpoint {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 10px 12px;
      border-radius: 7px;
      border: 1px solid var(--border);
      margin-bottom: 8px;
      font-size: 0.8rem;
      transition: border-color 0.2s, background 0.2s;
      cursor: default;
    }

    .endpoint:hover {
      background: var(--surface2);
      border-color: var(--border-bright);
    }

    .method {
      font-size: 0.6rem;
      font-weight: 500;
      letter-spacing: 0.08em;
      padding: 2px 6px;
      border-radius: 3px;
      min-width: 36px;
      text-align: center;
    }

    .get { background: rgba(99,210,143,0.12); color: var(--green); }
    .post { background: rgba(240,180,41,0.12); color: var(--amber); }

    .path { color: var(--text); flex: 1; }
    .desc { color: var(--text-muted); font-size: 0.72rem; }

    /* ── Feed ── */
    .feed { min-height: 60px; }

    .msg {
      display: flex;
      gap: 14px;
      padding: 14px 0;
      border-bottom: 1px solid var(--border);
      animation: slideIn 0.3s ease both;
    }

    .msg:last-child { border-bottom: none; }

    .msg-avatar {
      width: 32px;
      height: 32px;
      border-radius: 7px;
      background: linear-gradient(135deg, var(--green-dim), #1a3a2a);
      border: 1px solid var(--border-bright);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--sans);
      font-weight: 700;
      font-size: 0.75rem;
      color: var(--green);
      flex-shrink: 0;
    }

    .msg-content { flex: 1; min-width: 0; }

    .msg-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 3px;
    }

    .msg-author {
      font-family: var(--sans);
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text);
    }

    .msg-time {
      font-size: 0.68rem;
      color: var(--text-muted);
    }

    .msg-body {
      font-size: 0.83rem;
      color: #94a3b8;
      word-break: break-word;
    }

    .empty {
      text-align: center;
      padding: 32px 0;
      color: var(--text-muted);
      font-size: 0.8rem;
    }

    .empty-icon { font-size: 1.5rem; margin-bottom: 8px; opacity: 0.4; }

    /* ── Toast ── */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--surface2);
      border: 1px solid var(--border-bright);
      color: var(--green);
      padding: 12px 20px;
      border-radius: 8px;
      font-size: 0.8rem;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      transform: translateY(80px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
      z-index: 100;
      pointer-events: none;
    }

    .toast.show { transform: translateY(0); opacity: 1; }

    /* ── Footer ── */
    footer {
      margin-top: 48px;
      padding-top: 20px;
      border-top: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-size: 0.68rem;
      color: var(--text-muted);
      animation: fadeUp 0.6s 0.4s ease both;
    }

    .version-tag {
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text-muted);
    }

    /* ── Animations ── */
    @keyframes fadeDown {
      from { opacity: 0; transform: translateY(-16px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes fadeUp {
      from { opacity: 0; transform: translateY(16px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
      from { opacity: 0; transform: translateX(-10px); }
      to   { opacity: 1; transform: translateX(0); }
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%       { opacity: 0.5; transform: scale(0.85); }
    }

    /* ── Responsive ── */
    @media (max-width: 620px) {
      .grid { grid-template-columns: 1fr; }
      .stats { grid-template-columns: 1fr 1fr; }
      .header-top { flex-direction: column; align-items: flex-start; gap: 12px; }
    }
  </style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <header>
    <div class="header-top">
      <div class="logo">
        <div class="logo-icon">⬡</div>
        <div>
          <h1>DevOps Demo</h1>
        </div>
      </div>
      <div class="status-bar">
        <div class="badge"><span class="dot"></span> Live</div>
        <div class="badge"><span class="dot amber"></span> Blue slot</div>
      </div>
    </div>
    <p class="tagline">CI/CD · Blue-Green Deploy · IaC · Monitoring</p>
  </header>

  <!-- Stats -->
  <div class="stats">
    <div class="stat">
      <div class="stat-label">Messages</div>
      <div class="stat-value" id="msg-count">0</div>
    </div>
    <div class="stat">
      <div class="stat-label">Version</div>
      <div class="stat-value neutral" id="app-version">—</div>
    </div>
    <div class="stat">
      <div class="stat-label">Status</div>
      <div class="stat-value">OK</div>
    </div>
  </div>

  <!-- Main grid -->
  <div class="grid">

    <!-- Post message -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">Post Message</span>
      </div>
      <div class="field">
        <label>Author</label>
        <input type="text" id="author" placeholder="Your name" maxlength="40" />
      </div>
      <div class="field">
        <label>Message</label>
        <textarea id="body" placeholder="Write something..."></textarea>
      </div>
      <button class="btn" id="submit-btn" onclick="postMsg()">Send Message</button>
    </div>

    <!-- API endpoints -->
    <div class="card">
      <div class="card-header">
        <span class="card-title">API Endpoints</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="path">/health</span>
        <span class="desc">Health check</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="path">/api/messages</span>
        <span class="desc">List messages</span>
      </div>
      <div class="endpoint">
        <span class="method post">POST</span>
        <span class="path">/api/messages</span>
        <span class="desc">Post message</span>
      </div>
      <div class="endpoint">
        <span class="method get">GET</span>
        <span class="path">/api/echo/:name</span>
        <span class="desc">Dynamic route</span>
      </div>
    </div>

    <!-- Message feed -->
    <div class="card card-full">
      <div class="card-header">
        <span class="card-title">Live Feed</span>
        <span class="badge"><span class="dot"></span> Auto-refresh 5s</span>
      </div>
      <div class="feed" id="feed">
        <div class="empty">
          <div class="empty-icon">◈</div>
          No messages yet — post the first one!
        </div>
      </div>
    </div>

  </div>

  <!-- Footer -->
  <footer>
    <span>DevOps Demo App · Flask + Python</span>
    <span class="version-tag">⬡ Blue-Green Deployment</span>
  </footer>

</div>

<!-- Toast -->
<div class="toast" id="toast"></div>

<script>
  // Load version on start
  fetch('/health').then(r => r.json()).then(d => {
    document.getElementById('app-version').textContent = d.version || '1.0.0';
  }).catch(() => {});

  function showToast(msg, isError = false) {
    const t = document.getElementById('toast');
    t.textContent = msg;
    t.style.color = isError ? 'var(--red)' : 'var(--green)';
    t.style.borderColor = isError ? 'rgba(245,101,101,0.3)' : 'rgba(99,210,143,0.3)';
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2800);
  }

  async function postMsg() {
    const author = document.getElementById('author').value.trim() || 'Anonymous';
    const body = document.getElementById('body').value.trim();
    if (!body) { showToast('Message cannot be empty', true); return; }

    const btn = document.getElementById('submit-btn');
    btn.classList.add('loading');
    btn.textContent = 'Sending...';

    try {
      const res = await fetch('/api/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ author, body })
      });
      if (res.ok) {
        document.getElementById('body').value = '';
        showToast('✓ Message posted');
        await loadFeed();
      } else {
        showToast('Failed to post', true);
      }
    } catch {
      showToast('Network error', true);
    }

    btn.classList.remove('loading');
    btn.textContent = 'Send Message';
  }

  async function loadFeed() {
    try {
      const res = await fetch('/api/messages');
      const data = await res.json();
      const feed = document.getElementById('feed');
      document.getElementById('msg-count').textContent = data.messages.length;

      if (data.messages.length === 0) {
        feed.innerHTML = '<div class="empty"><div class="empty-icon">◈</div>No messages yet — post the first one!</div>';
        return;
      }

      feed.innerHTML = [...data.messages].reverse().map(m => {
        const initial = (m.author || '?')[0].toUpperCase();
        return `
          <div class="msg">
            <div class="msg-avatar">${initial}</div>
            <div class="msg-content">
              <div class="msg-meta">
                <span class="msg-author">${esc(m.author)}</span>
                <span class="msg-time">${esc(m.timestamp)}</span>
              </div>
              <div class="msg-body">${esc(m.body)}</div>
            </div>
          </div>`;
      }).join('');
    } catch {}
  }

  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }

  // Enter to submit
  document.getElementById('body').addEventListener('keydown', e => {
    if (e.key === 'Enter' && e.ctrlKey) postMsg();
  });

  loadFeed();
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