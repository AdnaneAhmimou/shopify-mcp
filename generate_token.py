"""
Run this script ONCE to generate your Google OAuth refresh token.
It will open a browser, you log in and approve, then it prints the token.

Usage:
    pip install google-auth-oauthlib
    python generate_token.py
"""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",   # Search Console
    "https://www.googleapis.com/auth/analytics.readonly",    # Google Analytics
    "https://www.googleapis.com/auth/content",               # Merchant Center
]

flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
creds = flow.run_local_server(port=0)

print("\n" + "="*60)
print("Copy these values into your .env file on the VPS:")
print("="*60)
print(f"GOOGLE_CLIENT_ID={creds.client_id}")
print(f"GOOGLE_CLIENT_SECRET={creds.client_secret}")
print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
print("="*60 + "\n")
