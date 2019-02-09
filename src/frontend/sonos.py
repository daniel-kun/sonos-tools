from datetime import datetime
from datetime import timedelta
import os
import db
import uuid

from flask import request
import requests

SONOSTOOLS_SONOSAPI_APPKEY = os.environ['SONOSTOOLS_SONOSAPI_APPKEY']
SONOSTOOLS_SONOSAPI_SECRET = os.environ['SONOSTOOLS_SONOSAPI_SECRET']

def sonosPlayClip(dbClient, apiKey, sonosAccessToken, sonosRefreshToken, sonosPlayerId, uri):
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

def sonosAuth(dbClient, sonosAuthCode, accountid):
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
    players = sonosMergePlayerApiKeys([], sonosListPlayers(sonosAccessToken, sonosRefreshToken))
    return db.update_account_sonos_tokens(dbClient, accountid, {
        "access_token": sonosAccessToken,
        "refresh_token": sonosRefreshToken,
        "scope": sonosScope,
        "expires_at": sonosExpiresAt,
        "players": players
    })

def sonosListPlayers(sonosAccessToken, sonosRefreshToken):
    households = requests.get("https://api.ws.sonos.com/control/api/v1/households",
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }).json()
    playerIds = []
    for household in households['households']:
        householdId = household['id']
        groups = requests.get('https://api.ws.sonos.com/control/api/v1/households/{0}/groups'.format(householdId),
            headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }).json()
        for player in groups['players']:
            playerIds.append(player['id'])
    return playerIds

def sonosMergePlayerApiKeys(players, playerIds):
    playerApiKeyDict = {item['playerId']:item['apiKey'] for item in players}
    def getApiKey(playerId):
        if playerId in playerApiKeyDict:
            return playerApiKeyDict[playerId]
        else:
            return str(uuid.uuid4())
    return [{'playerId': playerId, 'apiKey': getApiKey(playerId)} for playerId in playerIds]

def sonosUpdatePlayerApiKeys(dbClient, accountid):
    account = db.find_account_id(dbClient, accountid)
    playerIds = sonosListPlayers(account['sonos']['access_token'], account['sonos']['refresh_token'])
    db.update_account_sonos_players(dbClient, accountid, sonosMergePlayerApiKeys(account['sonos']['players'], playerIds))

