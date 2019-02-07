from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask.json import jsonify
from google.oauth2 import id_token
from google.auth.transport import requests
import os

import db
import text_to_speech as tts

app = Flask(__name__)

SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID=os.environ['SONOSTOOLS_GOOGLE_AUTH_CLIENT_ID']
SONOSTOOLS_GOOGLE_AUTH_CLIENTFILE=os.environ['SONOSTOOLS_GOOGLE_AUTH_CLIENTFILE']

SONOSTOOLS_GCP_API_KEY = os.environ['SONOSTOOLS_GCP_API_KEY']
SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']
SONOSTOOLS_SONOSAPI_PLAYERID = os.environ['SONOSTOOLS_SONOSAPI_PLAYERID']

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

def execSonos(apiKey, sonosAccessToken, sonosRefreshToken, sonosPlayerId, audioConfigHash):
    headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
    body = {
        "name": "Demo Clip",
        "appId": "com.acme.com",
        "streamUrl": "http://hr8jeljvudseiccl8kzrps.webrelay.io/audioFile/{0}".format(audioConfigHash)
    }
    request = requests.post("https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip".format(sonosPlayerId),
            headers=headers,
            json=body)
    if request.status_code == 401:
        print("Sonos API token not valid, trying to refresh")
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
        refreshRequest = requests.post("https://api.sonos.com/login/v3/oauth/access", headers=headers, data={
            "grant_type": "refresh_token",
            "refresh_token": sonosRefreshToken
        })
        if refreshRequest.status_code != 200:
            print(sonosRefreshToken)
            print(refreshRequest)
            raise Exception("Sonos API Access Token invalid and could not be refreshed.")
        sonosAccessToken = refreshRequest['access_token']
        sonosRefreshToken = refreshRequest['refresh_token']
        db.update_apikey(dbClient, apiKey, sonosAccessToken, sonosRefreshToken)
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
        print("Refreshed Sonos API token")
        return requests.post("https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip".format(sonosPlayerId),
                headers=headers,
                json=body)
        pass
    return request

def getTextToSpeechHash(client, languageCode, text, apiKey):
    audioConfigHash = tts.textToAudioConfigHash(languageCode, text)
    audio = db.find_audio(client, audioConfigHash)
    if audio == None:
        (audioConfigHash, audioFile) = tts.textToSpeech(languageCode, text, apiKey)
        db.insert_audio(client, audioConfigHash, audioFile)
        return (audioConfigHash, False)
    else:
        return (audioConfigHash, True)

@app.route("/api/v1/synthesize", methods=['POST'])
def synthesize():
    payload = request.json 
    dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
    (audioConfigHash, fromCache) = getTextToSpeechHash(dbClient, payload['languageCode'], payload['text'], SONOSTOOLS_GCP_API_KEY)
    return jsonify(audioConfigHash=audioConfigHash, fromCache=fromCache)

@app.route("/api/v1/speak", methods=['POST'])
def speak():
    try:
        payload = request.json 
        if not ('key' in payload and 'text' in payload and 'languageCode' in payload):
            raise Exception('Fields "key", "languageCode" and "text" must be included in the request')

        apiKeyDoc = db.find_apikey(dbClient, payload['key'])
        if apiKeyDoc == None:
            raise Exception('Invalid "key"')

        (audioConfigHash, fromCache) = getTextToSpeechHash(dbClient, payload['languageCode'], payload['text'], SONOSTOOLS_GCP_API_KEY)
        result = execSonos(payload['key'], apiKeyDoc['sonosAccessToken'], apiKeyDoc['sonosRefreshToken'], SONOSTOOLS_SONOSAPI_PLAYERID, audioConfigHash)
        if result.status_code == 200:
            if fromCache:
                return make_response("Roger, playing sound (from cache)", 200)
            else:
                return make_response("Roger, playing sound (synthesized just for you!)", 200)
        else:
            make_response("Failed to play sound", 500)
    except Exception as err:
        make_response(str(err), 401)

@app.route("/audioFile/<audioConfigHash>")
def audioFile(audioConfigHash):
    audioFile = db.find_audio(dbClient, audioConfigHash)
    if audioFile != None:
        return make_response((audioFile, 200, {'Content-Type': 'audio/mpeg'}))
    else:
        return make_response("<html><body><h1>Could not find this audio file</h1>", 404)

@app.route("/sonos_auth/")
def sonosAuth():
    raise Exception("Not implemented, yet")

dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)

