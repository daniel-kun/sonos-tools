from datetime import datetime
from datetime import timedelta
import os
import db
import uuid

from flask import request
import requests

SONOSTOOLS_SONOSAPI_APPKEY = os.environ['SONOSTOOLS_SONOSAPI_APPKEY']
SONOSTOOLS_SONOSAPI_SECRET = os.environ['SONOSTOOLS_SONOSAPI_SECRET']
SONOSTOOLS_SONOSAPI_ENDPOINT = os.environ['SONOSTOOLS_SONOSAPI_ENDPOINT']
SONOSTOOLS_SONOSAPI_ENDPOINT_WS = os.environ['SONOSTOOLS_SONOSAPI_ENDPOINT_WS']
SONOSTOOLS_REDIRECT_ROOT = os.environ['SONOSTOOLS_REDIRECT_ROOT']

def sonosPlayClip(dbClient, accountid, apiKey, sonosAccessToken, sonosRefreshToken, playerId, uri, logger):
    try:
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
        body = {
            "name": "Demo Clip",
            "appId": "com.acme.com",
            "streamUrl": uri 
        }
        url = "{0}/control/api/v1/players/{1}/audioClip".format(SONOSTOOLS_SONOSAPI_ENDPOINT_WS, playerId)
        logger.info('Making clip request to "{0}"\nHeaders: {1}\nBody: {2}'.format(url, headers, body))
        request = requests.post(url, headers=headers, json=body)
        logger.info('Response: {0}\n{1}'.format(request.status_code, request.text))
        if request.status_code == 401:
            print("Sonos API token not valid, trying to refresh")
            refreshRequest = requests.post("{0}/login/v3/oauth/access".format(SONOSTOOLS_SONOSAPI_ENDPOINT), headers=headers, data={
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
            db.update_apikey(dbClient, accountid, sonosAccessToken, sonosRefreshToken)
            print("Refreshed Sonos API token")
            headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
            audioClipRequest = requests.post("{0}/control/api/v1/players/{1}/audioClip".format(SONOSTOOLS_SONOSAPI_ENDPOINT_WS, playerId),
                    headers=headers,
                    json=body)
            if audioClipRequest.status_code != 200:
                print(sonosAccessToken)
                print(refreshRequest)
                raise Exception("Sonos audioClip request failed with status code {0}:\n{1}.".format(audioClipRequest.status_code, audioClipRequest.text))
            return audioClipRequest
        return request
    except Exception as err:
        print(err)
        raise err

def sonosAuth(dbClient, sonosAuthCode, accountid, logger):
    postData = {
        "grant_type": "authorization_code",
        "code": sonosAuthCode,
        "redirect_uri": '{0}/sonos_auth'.format(SONOSTOOLS_REDIRECT_ROOT)
    }
    url = '{0}/login/v3/oauth/access'.format(SONOSTOOLS_SONOSAPI_ENDPOINT)
    logger.info('Trying {0} with data {1}'.format(url, postData))
    print('Trying {0} with data {1}'.format(url, postData))
    request = requests.post( url, data=postData, auth=(SONOSTOOLS_SONOSAPI_APPKEY, SONOSTOOLS_SONOSAPI_SECRET))
    logger.info('Received status code {0}, body {1}'.format(request.status_code, request.text))
    print('Received status code {0}, body {1}'.format(request.status_code, request.text))
    r = request.json()
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
    households = requests.get("{0}/control/api/v1/households".format(SONOSTOOLS_SONOSAPI_ENDPOINT_WS),
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }).json()
    playerIds = []
    for household in households['households']:
        householdId = household['id']
        groups = requests.get('{0}/control/api/v1/households/{1}/groups'.format(SONOSTOOLS_SONOSAPI_ENDPOINT_WS, householdId),
            headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }).json()
        for player in groups['players']:
            playerIds.append({"playerId": player['id'], "name": player['name']})
    return playerIds

def sonosMergePlayerApiKeys(players, playerIds):
    playerApiKeyDict = {item['playerId']:item['apiKey'] for item in players}
    def getApiKey(playerId):
        if playerId in playerApiKeyDict:
            return playerApiKeyDict[playerId]
        else:
            return str(uuid.uuid4())
    return [{'playerId': playerId['playerId'], 'name': playerId['name'], 'apiKey': getApiKey(playerId['playerId'])} for playerId in playerIds]

def sonosUpdatePlayerApiKeys(dbClient, accountid):
    account = db.find_account_id(dbClient, accountid)
    playerIds = sonosListPlayers(account['sonos']['access_token'], account['sonos']['refresh_token'])
    db.update_account_sonos_players(dbClient, accountid, sonosMergePlayerApiKeys(account['sonos']['players'], playerIds))

