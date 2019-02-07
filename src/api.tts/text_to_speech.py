import os
import json
import requests
import base64
import hashlib

def _hash(obj):
    hasher = hashlib.sha256()
    hasher.update(json.dumps(obj).encode('utf-8'))
    return hasher.hexdigest()

def textToAudioConfig(languageCode, text):
    return {
        'input': { 'text': text },
        'voice': { 'languageCode': languageCode },
        'audioConfig': { 'audioEncoding': 'MP3' }
    }

def textToAudioConfigHash(languageCode, text):
    return _hash(textToAudioConfig(languageCode, text))

def textToSpeech(languageCode, text, apiKey):
    audioConfig = textToAudioConfig(languageCode, text)
    req = requests.post('https://texttospeech.googleapis.com/v1/text:synthesize?key={key}'.format(key=apiKey), json=audioConfig)
    result = req.json()
    if 'audioContent' in result:
        return (_hash(audioConfig), base64.b64decode(result['audioContent']))
    else:
        raise Exception('Could not synthesize speech using Google Cloud.', req.text)

