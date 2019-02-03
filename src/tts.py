import os
import requests
import base64

def textToSpeech(languageCode, text, apiKey):
    req = requests.post('https://texttospeech.googleapis.com/v1/text:synthesize?key={key}'.format(key=apiKey), json={
        'input': { 'text': text },
        'voice': { 'languageCode': languageCode },
        'audioConfig': { 'audioEncoding': 'MP3' } })
    result = req.json()
    if 'audioContent' in result:
        return base64.b64decode(result['audioContent'])
    else:
        raise Exception('Could not synthesize speech using Google Cloud.', req.text)

