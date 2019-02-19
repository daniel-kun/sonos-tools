import pymongo
from pymongo import MongoClient
from bson import ObjectId
import base64

def connect(connectUri):
    return MongoClient(connectUri)

def create_indexes(client):
    db = client['sonos-tools']
    accounts = db['accounts']
    accounts.create_indexes([("auth_type", pymongo.ASCENDING), ("userid", pymongo.ASCENDING)], unique = True)
    audioFiles = db['audio-files']
    return audioFiles.create_index([("audioConfigHash", pymongo.ASCENDING)], unique = True)

def find_apikey(client, apiKey):
    db = client['sonos-tools']
    accounts = db['accounts']
    account = accounts.find_one({"sonos.players.apiKey": apiKey})
    if account == None:
        return None
    return ({
        "accountid": str(account['_id']),
        "access_token": account['sonos']['access_token'],
        "refresh_token": account['sonos']['refresh_token'],
        "playerId": next(player['playerId'] for player in account['sonos']['players'] if player['apiKey'] == apiKey),
        "apiKey": apiKey
    })

def update_apikey(client, accountid, sonosAccessToken, sonosRefreshToken):
    print('accountid: {0}, sonosAccessToken: {1}, sonosRefreshToken: {2}'.format(accountid, sonosAccessToken, sonosRefreshToken))
    db = client['sonos-tools']
    accounts = db['accounts']
    result = accounts.update_one({
            '_id': ObjectId(accountid)
        },
        {
            '$set': {
                'sonos.access_token': sonosAccessToken,
                'sonos.refresh_token': sonosRefreshToken
            }
        })
    return result

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

def update_account_sonos_players(client, accountid, players):
    db = client['sonos-tools']
    accounts = db['accounts']
    return accounts.update_one({'_id': ObjectId(accountid)}, { '$set': { 'sonos.players': players} })

def update_account_logout_sonos(client, accountid):
    db = client['sonos-tools']
    accounts = db['accounts']
    return accounts.update_one({'_id': ObjectId(accountid)}, { '$unset': { 'sonos': '' } })

