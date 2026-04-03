"""
Google OAuth Setup Server
Run this temporarily on the VPS to authorize Google access.
Visit http://YOUR_VPS_IP:8001 to start the flow.

Usage on VPS:
    pip install google-auth-oauthlib flask requests
    python oauth_setup.py
"""
import os
import json
import requests
from flask import Flask, redirect, request, render_template_string

app = Flask(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/content",
]

CREDENTIALS_FILE = "credentials.json"

with open(CREDENTIALS_FILE) as f:
    creds_data = json.load(f)

CLIENT_ID     = creds_data["installed"]["client_id"]
CLIENT_SECRET = creds_data["installed"]["client_secret"]
REDIRECT_URI  = "urn:ietf:wg:oauth:2.0:oob"
AUTH_URL      = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL     = "https://oauth2.googleapis.com/token"

AUTH_PAGE = """
<html><body style='font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px'>
    <h2>Google Authorization — Shopify MCP</h2>
    <p>Click the button below to authorize access to:</p>
    <ul>
        <li>✅ Google Search Console</li>
        <li>✅ Google Analytics 4</li>
        <li>✅ Google Merchant Center</li>
    </ul>
    <a href="{{ auth_url }}" style='background:#4285f4;color:white;padding:12px 24px;text-decoration:none;border-radius:4px;display:inline-block'>
        Authorize with Google
    </a>
</body></html>
"""

CODE_PAGE = """
<html><body style='font-family:sans-serif;max-width:600px;margin:50px auto;padding:20px'>
    <h2>Step 2 — Paste Authorization Code</h2>
    <p>After approving on Google, you'll see a code. Paste it below:</p>
    <form method='POST' action='/save'>
        <input name='code' placeholder='Paste code here' style='width:100%;padding:10px;font-size:14px;margin-bottom:10px'>
        <br>
        <button type='submit' style='background:#4285f4;color:white;padding:12px 24px;border:none;border-radius:4px;font-size:16px;cursor:pointer'>
            Save Token
        </button>
    </form>
</body></html>
"""

SUCCESS_PAGE = """
<html><body style='font-family:sans-serif;text-align:center;padding:50px'>
    <h1 style='color:green'>✅ Authorization Successful!</h1>
    <p>Google access has been granted for:</p>
    <ul style='list-style:none;padding:0'>
        <li>✅ Google Search Console</li>
        <li>✅ Google Analytics 4</li>
        <li>✅ Google Merchant Center</li>
    </ul>
    <p>The refresh token has been saved on the server.</p>
    <p><strong>You can close this window.</strong></p>
</body></html>
"""

ERROR_PAGE = """
<html><body style='font-family:sans-serif;text-align:center;padding:50px'>
    <h1 style='color:red'>❌ Error</h1>
    <p>{{ error }}</p>
    <a href='/'>Try again</a>
</body></html>
"""


@app.route("/")
def index():
    scope_str = " ".join(SCOPES)
    auth_url = (
        f"{AUTH_URL}?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={scope_str}"
        f"&access_type=offline"
        f"&prompt=consent"
    )
    return render_template_string(AUTH_PAGE, auth_url=auth_url)


@app.route("/code")
def code_page():
    return CODE_PAGE


@app.route("/save", methods=["POST"])
def save():
    code = request.form.get("code", "").strip()
    if not code:
        return render_template_string(ERROR_PAGE, error="No code provided.")

    # Exchange code for tokens
    resp = requests.post(TOKEN_URL, data={
        "code":          code,
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri":  REDIRECT_URI,
        "grant_type":    "authorization_code",
    })

    if resp.status_code != 200:
        return render_template_string(ERROR_PAGE, error=f"Token exchange failed: {resp.text}")

    token_data = resp.json()
    refresh_token = token_data.get("refresh_token")
    if not refresh_token:
        return render_template_string(ERROR_PAGE, error="No refresh token returned. Try revoking access at myaccount.google.com/permissions and try again.")

    # Save to google_token.json
    with open("google_token.json", "w") as f:
        json.dump({"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "refresh_token": refresh_token}, f, indent=2)

    # Update .env
    env_lines = []
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            env_lines = [l for l in f.readlines() if not l.startswith("GOOGLE_")]
    env_lines += [
        f"\nGOOGLE_CLIENT_ID={CLIENT_ID}\n",
        f"GOOGLE_CLIENT_SECRET={CLIENT_SECRET}\n",
        f"GOOGLE_REFRESH_TOKEN={refresh_token}\n",
    ]
    with open(".env", "w") as f:
        f.writelines(env_lines)

    return SUCCESS_PAGE


if __name__ == "__main__":
    print("\n" + "="*60)
    print("OAuth Setup Server running!")
    print("Send this link to the client:")
    print("http://91.108.122.206:8001")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=8001, debug=False)
