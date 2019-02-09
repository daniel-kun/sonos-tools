import pymongo
from pymongo import MongoClient
from bson import ObjectId
import base64

def connect(connectUri):
    return MongoClient(connectUri)

def create_indexes(client):
    db = client['sonos-tools']
    tokens = db['tokens']
    tokens.create_indexes([("apiKey", pymongo.ASCENDING)], unique = True)
    accounts = db['accounts']
    accounts.create_indexes([("auth_type", pymongo.ASCENDING), ("userid", pymongo.ASCENDING)], unique = True)
    audioFiles = db['audio-files']
    return audioFiles.create_index([("audioConfigHash", pymongo.ASCENDING)], unique = True)

def find_apikey(client, apiKey):
    db = client['sonos-tools']
    tokens = db['tokens']
    return tokens.find_one({"apiKey": apiKey})

def update_apikey(client, apiKey, sonosAccessToken, sonosRefreshToken):
    db = client['sonos-tools']
    tokens = db['tokens']
    return tokens.replace_one({
            "apiKey": apiKey
        },
        {
            "apiKey": apiKey,
            "sonosAccessToken": sonosAccessToken,
            "sonosRefreshToken": sonosRefreshToken
        })

def find_account(client, userid):
    db = client['sonos-tools']
    accounts = db['accounts']
    return accounts.find_one({
        'auth_type': 'Google',
        'userid': userid
    })

def find_account_id(client, accountid):
    db = client['sonos-tools']
    accounts = db['accounts']
    return accounts.find_one({
        '_id': ObjectId(accountid)
    })

def insert_account(client, account):
    db = client['sonos-tools']
    accounts = db['accounts']
    return accounts.insert_one(account)

def update_account_sonos_tokens(client, accountid, sonosData):
    db = client['sonos-tools']
    accounts = db['accounts']
    return accounts.update_one({'_id': ObjectId(accountid)}, { '$set': { 'sonos': sonosData } })

def update_account_logout_sonos(client, accountid):
    db = client['sonos-tools']
    accounts = db['accounts']
    return accounts.update_one({'_id': ObjectId(accountid)}, { '$unset': { 'sonos': '' } })

