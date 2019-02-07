from flask import Flask
from flask import render_template
from flask import make_response
from flask import request
from flask.json import jsonify
import os

import db
import text_to_speech as tts

app = Flask(__name__)

SONOSTOOLS_GCP_API_KEY = os.environ['SONOSTOOLS_GCP_API_KEY']
SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']

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
    try:
        dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
        payload = request.json 
        languageCode = payload['languagecode']
        text = payload['text']
        apiKey = db.find_apikey(dbClient, payload['apikey'])
        if apiKey == None:
            return make_response('Invalid apikey', 401)
    except Exception as err:
        print(err)
        return make_response('Invalid request', 500)
    (audioConfigHash, fromCache) = getTextToSpeechHash(dbClient, languageCode, text, SONOSTOOLS_GCP_API_KEY)
    return jsonify(audioConfigHash=audioConfigHash, fromCache=fromCache, uri='{0}audio/{1}'.format(request.url_root, audioConfigHash))

@app.route("/audio/<audioConfigHash>")
def audioFile(audioConfigHash):
    audioFile = db.find_audio(dbClient, audioConfigHash)
    if audioFile != None:
        return make_response((audioFile, 200, {'Content-Type': 'audio/mpeg'}))
    else:
        return make_response("<html><body><h1>Could not find this audio file</h1>", 404)

dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)

