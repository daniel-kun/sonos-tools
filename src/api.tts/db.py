import pymongo
from pymongo import MongoClient
import base64

def connect(connectUri):
    return MongoClient(connectUri)

def find_apikey(client, apiKey):
    db = client['sonos-tools']
    tokens = db['tokens']
    return tokens.find_one({"apiKey": apiKey})

def find_audio(client, audioConfigHash):
    db = client['sonos-tools']
    audioFiles = db['audio-files']
    result = audioFiles.find_one({"audioConfigHash": audioConfigHash})
    if result == None:
        return None
    else:
        return base64.b64decode(result['audioFile'])

def insert_audio(client, audioConfigHash, audioFile):
    db = client['sonos-tools']
    audioFiles = db['audio-files']
    return audioFiles.insert_one({
            "audioConfigHash": audioConfigHash,
            "audioFile": base64.b64encode(audioFile)
        })

def remove_audio(client, audioConfigHash):
    db = client['sonos-tools']
    audioFiles = db['audio-files']
    return audioFiles.delete_one({
            "audioConfigHash": audioConfigHash
        })

