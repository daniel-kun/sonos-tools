from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from google.oauth2 import id_token
from google.auth.transport import requests
import os
app = Flask(__name__)

SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID=os.environ['SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID']
SONOSTOOLS_GOOGLE_AUTH_CLIENTFILE=os.environ['SONOSTOOLS_GOOGLE_AUTH_CLIENTFILE']

@app.route("/")
def index():
    return render_template('index.html', google_auth_client_id=SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID)

@app.route("/receive_google_auth", methods=['POST'])
def receive_google_auth():
    payload = request.json
    print(payload)
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(payload['token'], requests.Request(), SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        print(userid)
    except ValueError:
        # Invalid token
        pass
    return make_response('Success', 200)

