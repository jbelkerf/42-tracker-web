"""
42 Login Tracker - Auth Server
Hosted on Vercel. Handles the OAuth2 flow and returns the token to the user.
"""

from flask import Flask, redirect, request, render_template_string
import requests
import os

app = Flask(__name__)

CLIENT_ID     = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
REDIRECT_URI  = os.environ["REDIRECT_URI"]   # e.g. https://yourapp.vercel.app/callback

AUTH_URL  = "https://api.intra.42.fr/oauth/authorize"
TOKEN_URL = "https://api.intra.42.fr/oauth/token"

# ── Pages ──────────────────────────────────────────────────────────────────────

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>42 Login Tracker</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #0f0f0f;
      color: #eee;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 2rem;
    }
    h1 { font-size: 2rem; margin-bottom: 0.5rem; }
    p  { color: #aaa; margin-bottom: 2rem; text-align: center; }
    a.btn {
      background: #00babc;
      color: #000;
      font-weight: bold;
      padding: 0.9rem 2rem;
      border-radius: 8px;
      text-decoration: none;
      font-size: 1rem;
      transition: opacity 0.2s;
    }
    a.btn:hover { opacity: 0.85; }
    .steps {
      margin-top: 3rem;
      background: #1a1a1a;
      border-radius: 10px;
      padding: 1.5rem 2rem;
      max-width: 480px;
      width: 100%;
    }
    .steps h2 { font-size: 1rem; color: #aaa; margin-bottom: 1rem; }
    .steps ol { padding-left: 1.2rem; line-height: 2; color: #ccc; font-size: 0.95rem; }
    code {
      background: #2a2a2a;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.9rem;
      color: #00babc;
    }
  </style>
</head>
<body>
  <h1>42 Login Tracker</h1>
  <p>Authenticate with your 42 intra account to get your token.</p>
  <a class="btn" href="/login">Login with 42 Intra</a>

  <div class="steps">
    <h2>How it works</h2>
    <ol>
      <li>Click the button above and log in with your 42 account</li>
      <li>Copy the token shown after login</li>
      <li>Run <code>./launch.sh &lt;peer&gt; &lt;logged|delogged&gt;</code></li>
      <li>Paste the token when prompted</li>
    </ol>
  </div>
</body>
</html>
"""

TOKEN_HTML = """
<!DOCTYPE html>
<html>
<head>
  <title>Your Token - 42 Tracker</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #0f0f0f;
      color: #eee;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 2rem;
    }
    h1 { font-size: 1.8rem; margin-bottom: 0.5rem; }
    .subtitle { color: #aaa; margin-bottom: 2rem; }
    .token-box {
      background: #1a1a1a;
      border: 1px solid #333;
      border-radius: 10px;
      padding: 1.5rem;
      max-width: 560px;
      width: 100%;
      word-break: break-all;
      font-family: monospace;
      font-size: 0.95rem;
      color: #00babc;
      margin-bottom: 1rem;
      cursor: pointer;
      position: relative;
    }
    .copy-btn {
      background: #00babc;
      color: #000;
      font-weight: bold;
      border: none;
      padding: 0.8rem 1.8rem;
      border-radius: 8px;
      cursor: pointer;
      font-size: 1rem;
      margin-bottom: 2rem;
    }
    .copy-btn:hover { opacity: 0.85; }
    .warning {
      background: #1a1200;
      border: 1px solid #554400;
      border-radius: 8px;
      padding: 1rem 1.5rem;
      max-width: 560px;
      width: 100%;
      color: #ccaa00;
      font-size: 0.9rem;
      line-height: 1.6;
    }
    #copied { display:none; color: #00babc; margin-bottom: 1rem; font-size: 0.95rem; }
  </style>
</head>
<body>
  <h1>✓ Logged in as {{ login }}</h1>
  <p class="subtitle">Copy this token and paste it into your terminal.</p>

  <div class="token-box" onclick="copyToken()">{{ token }}</div>
  <button class="copy-btn" onclick="copyToken()">Copy Token</button>
  <div id="copied">✓ Copied to clipboard!</div>

  <div class="warning">
    ⚠️ This token is valid for <strong>2 hours</strong>. After it expires,
    visit this page again to get a new one.<br><br>
    Do <strong>not</strong> share this token with anyone — it gives access to your 42 account data.
  </div>

  <script>
    function copyToken() {
      navigator.clipboard.writeText("{{ token }}");
      document.getElementById("copied").style.display = "block";
    }
  </script>
</body>
</html>
"""

ERROR_HTML = """
<!DOCTYPE html>
<html>
<head><title>Error - 42 Tracker</title>
<style>
  body { font-family: sans-serif; background:#0f0f0f; color:#eee;
         display:flex; flex-direction:column; align-items:center;
         justify-content:center; min-height:100vh; }
  .box { background:#1a1a1a; padding:2rem; border-radius:10px; max-width:480px; }
  h1 { color:#ff4444; margin-bottom:1rem; }
  a { color:#00babc; }
</style>
</head>
<body>
  <div class="box">
    <h1>Authentication Failed</h1>
    <p>{{ error }}</p>
    <br>
    <a href="/">← Try again</a>
  </div>
</body>
</html>
"""

# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template_string(HOME_HTML)


@app.route("/login")
def login():
    params = (
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=public"
    )
    return redirect(AUTH_URL + params)


@app.route("/callback")
def callback():
    code  = request.args.get("code")
    error = request.args.get("error")

    if error or not code:
        return render_template_string(ERROR_HTML, error=error or "No code received."), 400

    # Exchange code for token
    resp = requests.post(TOKEN_URL, data={
        "grant_type":    "authorization_code",
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code":          code,
        "redirect_uri":  REDIRECT_URI,
    })

    if resp.status_code != 200:
        return render_template_string(ERROR_HTML, error=f"Token exchange failed: {resp.text}"), 500

    token = resp.json().get("access_token")

    # Get the user's login to display on the page
    me_resp = requests.get(
        "https://api.intra.42.fr/v2/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    login_name = me_resp.json().get("login", "unknown") if me_resp.ok else "unknown"

    return render_template_string(TOKEN_HTML, token=token, login=login_name)
