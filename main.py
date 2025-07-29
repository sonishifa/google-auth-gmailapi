from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
import requests, os
from dotenv import load_dotenv
from urllib.parse import urlencode


load_dotenv()

app = FastAPI()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

@app.get("/")
def home():
    return HTMLResponse('<a href="/auth/login">Login with Google</a>')

@app.get("/auth/login")
def login():
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly",  # Added Gmail scope
        "access_type": "offline",
        "prompt": "consent"
    }
    query_string = urlencode(params)
    redirect_url = f"{google_auth_url}?{query_string}"
    return RedirectResponse(url=redirect_url)

@app.get("/auth/google/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    token_url = "https://oauth2.googleapis.com/token"

    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    token_response = requests.post(token_url, data=data)
    token_json = token_response.json()

    access_token = token_json.get("access_token")

    # Fetch Gmail profile
    gmail_profile_response = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/profile",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    gmail_profile = gmail_profile_response.json()

    return {
        "emailAddress": gmail_profile.get("emailAddress"),
        "messagesTotal": gmail_profile.get("messagesTotal")
    }
