from flask import Flask
from flask import render_template
from flask import make_response
from flask import url_for
from flask import request
from flask import redirect
from flask.json import jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
import os
import base64
import json
import requests
import db
import sonos
import account

app = Flask(__name__)

SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID=os.environ['SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID']
SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']
SONOSTOOLS_API_TTS_ROOT = os.environ['SONOSTOOLS_API_TTS_ROOT']
SONOSTOOLS_SONOSAPI_APPKEY = os.environ['SONOSTOOLS_SONOSAPI_APPKEY']
SONOSTOOLS_SONOSAPI_SECRET = os.environ['SONOSTOOLS_SONOSAPI_SECRET']

_dbClient = None

def dbClient():
    global _dbClient
    if _dbClient == None:
        _dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
    return _dbClient

@app.route("/")
def index():
    return render_template('index.html', google_auth_client_id=SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID)

@app.route("/receive_google_auth", methods=['POST'])
def receive_google_auth():
    payload = request.json
    print(payload)
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(payload['token'], grequests.Request(), SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        return jsonify(account.find_account_by_google_user_id(dbClient(), idinfo))

    except ValueError:
        return make_response('Invalid token', 401)
    return make_response('Success', 200)

@app.route("/api/v1/speak", methods=['POST'])
def speak():
    payload = request.json 
    if not ('key' in payload and 'text' in payload and 'languagecode' in payload):
        raise Exception('Fields "key", "languagecode" and "text" must be included in the request')

    apiKeyDoc = db.find_apikey(dbClient(), payload['key'])
    if apiKeyDoc == None:
        raise Exception('Invalid "key"')

    r = requests.post("{0}/api/v1/synthesize".format(SONOSTOOLS_API_TTS_ROOT), 
        json={
            'languagecode': payload['languagecode'],
            'text': payload['text'],
            'apikey': payload['key']
        })
    print(r.text)
    synResponse = r.json()
    audioConfigHash = synResponse['audioConfigHash']
    fromCache = synResponse['fromCache']
    uri = synResponse['uri']
    result = sonos.sonosPlayClip(dbClient(), apiKeyDoc['accountid'], apiKeyDoc['apiKey'], apiKeyDoc['access_token'], apiKeyDoc['refresh_token'], apiKeyDoc['playerId'], uri)
    if result.status_code == 200:
        if fromCache:
            return make_response("Roger, playing sound (from cache)", 200)
        else:
            return make_response("Roger, playing sound (synthesized just for you!)", 200)
    else:
        return make_response("Failed to play sound", 500)

@app.route("/sonos_auth")
def sonosAuth():
    sonosAuthCode = request.args.get('code')
    stateObj = json.loads(base64.b64decode(request.args.get('state')))
    accountid = stateObj['accountid']
    sonos.sonosAuth(dbClient(), sonosAuthCode, accountid)
    return redirect(url_for('index'))

@app.route("/db_init")
def db_init():
    return make_response(str(db.create_indexes(dbClient())), 200)

@app.route("/sonos_logout", methods=["POST"])
def sonosLogout():
    payload = request.json
    db.update_account_logout_sonos(dbClient(), payload['accountid'])
    return jsonify({'success': True})

