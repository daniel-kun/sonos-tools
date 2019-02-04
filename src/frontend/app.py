from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from apiclient import discovery
import httplib2
from oauth2client import client
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
    # Exchange auth code for access token, refresh token, and ID token
    credentials = client.credentials_from_clientsecrets_and_code(
            SONOSTOOLS_GOOGLE_AUTH_CLIENTFILE,
            ['profile', 'email'],
            payload['authCode'])

    # Get profile info from ID token
    print(credentials)
    print(credentials.id_token)
    userid = credentials.id_token['sub']
    email = credentials.id_token['email']
    return make_response('Success', 200)

