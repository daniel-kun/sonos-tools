from flask import Flask
from flask import render_template
from flask import make_response
from flask import url_for
from flask import request
from flask import redirect
from flask.json import jsonify
from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from datetime import datetime
from datetime import timedelta
import os
import base64
import json
import requests
import db
import account

app = Flask(__name__)

SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID=os.environ['SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID']
SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']
SONOSTOOLS_API_TTS_ROOT = os.environ['SONOSTOOLS_API_TTS_ROOT']
SONOSTOOLS_SONOSAPI_APPKEY = os.environ['SONOSTOOLS_SONOSAPI_APPKEY']
SONOSTOOLS_SONOSAPI_SECRET = os.environ['SONOSTOOLS_SONOSAPI_SECRET']
SONOSTOOLS_SONOSAPI_PLAYERID = os.environ['SONOSTOOLS_SONOSAPI_PLAYERID'] # This is only temporary until there is a UI to select the player

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
        return jsonify(account.find_account_by_google_user_id(idinfo))

    except ValueError:
        return make_response('Invalid token', 401)
    return make_response('Success', 200)

def execSonos(apiKey, sonosAccessToken, sonosRefreshToken, sonosPlayerId, uri):
    try:
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
        body = {
            "name": "Demo Clip",
            "appId": "com.acme.com",
            "streamUrl": uri 
        }
        request = requests.post("https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip".format(sonosPlayerId),
                headers=headers,
                json=body)
        if request.status_code == 401:
            print("Sonos API token not valid, trying to refresh")
            refreshRequest = requests.post("https://api.sonos.com/login/v3/oauth/access", headers=headers, data={
                "grant_type": "refresh_token",
                "refresh_token": sonosRefreshToken
            },
            auth=(SONOSTOOLS_SONOSAPI_APPKEY, SONOSTOOLS_SONOSAPI_SECRET))
            if refreshRequest.status_code != 200:
                print(sonosRefreshToken)
                print(refreshRequest)
                raise Exception("Sonos API Access Token invalid and could not be refreshed.")
            refreshResult = refreshRequest.json()
            sonosAccessToken = refreshResult['access_token']
            sonosRefreshToken = refreshResult['refresh_token']
            db.update_apikey(dbClient, apiKey, sonosAccessToken, sonosRefreshToken)
            headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
            print("Refreshed Sonos API token")
            return requests.post("https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip".format(sonosPlayerId),
                    headers=headers,
                    json=body)
            pass
        return request
    except Exception as err:
        print(err)
        raise err

@app.route("/api/v1/speak", methods=['POST'])
def speak():
    try:
        payload = request.json 
        if not ('key' in payload and 'text' in payload and 'languagecode' in payload):
            raise Exception('Fields "key", "languagecode" and "text" must be included in the request')

        apiKeyDoc = db.find_apikey(dbClient, payload['key'])
        if apiKeyDoc == None:
            raise Exception('Invalid "key"')

        r = requests.post("{0}/api/v1/synthesize".format(SONOSTOOLS_API_TTS_ROOT), 
            json={
                'languagecode': payload['languagecode'],
                'text': payload['text'],
                'apikey': payload['key']
            })
        synResponse = r.json()
        audioConfigHash = synResponse['audioConfigHash']
        fromCache = synResponse['fromCache']
        uri = synResponse['uri']
        result = execSonos(payload['key'], apiKeyDoc['sonosAccessToken'], apiKeyDoc['sonosRefreshToken'], SONOSTOOLS_SONOSAPI_PLAYERID, uri)
        if result.status_code == 200:
            if fromCache:
                return make_response("Roger, playing sound (from cache)", 200)
            else:
                return make_response("Roger, playing sound (synthesized just for you!)", 200)
        else:
            return make_response("Failed to play sound", 500)
    except Exception as err:
        return make_response(str(err), 401)

@app.route("/sonos_auth")
def sonosAuth():
    sonosAuthCode = request.args.get('code')
    stateObj = json.loads(base64.b64decode(request.args.get('state')))
    accountid = stateObj['accountid']
    postData = {
        "grant_type": "authorization_code",
        "code": sonosAuthCode,
        "redirect_uri": request.base_url
    }
    r = requests.post(
            'https://api.sonos.com/login/v3/oauth/access',
            data=postData,
            auth=(SONOSTOOLS_SONOSAPI_APPKEY, SONOSTOOLS_SONOSAPI_SECRET)).json()
    sonosAccessToken = r['access_token']
    sonosRefreshToken = r['refresh_token']
    sonosScope = r['scope']
    sonosExpiresAt = datetime.now() + timedelta(seconds=int(r['expires_in']))
    db.update_account_sonos_tokens(dbClient, accountid, {
        "access_token": sonosAccessToken,
        "refresh_token": sonosRefreshToken,
        "scope": sonosScope,
        "expires_at": sonosExpiresAt
    })
    return redirect(url_for('index'))

@app.route("/db_init")
def db_init():
    return make_response(str(db.create_indexes(dbClient)), 200)

dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)

