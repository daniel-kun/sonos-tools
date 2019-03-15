from flask import Flask
from flask import make_response
from flask import request
from flask import redirect
from flask import jsonify
from base64 import b64encode
from base64 import b64decode

app = Flask(__name__)

# TODO:
'''
https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip
    headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
    body = {
        "name": "Demo Clip",
        "appId": "com.acme.com",
        "streamUrl": uri 
    }
'''

def get_bearer_token(header):
    if header.startswith('Bearer '):
        return header[len('Bearer '):]
    else:
        return "";

'''
https://api.ws.sonos.com/control/api/v1/households/{0}/groups
    headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
'''
@app.route("/control/api/v1/households/<string:householdId>/groups", methods=["GET"])
def control_api_v1_households_groups(householdId):
    token = get_bearer_token(request.headers['Authorization'])
    if token == "XXX_TOKEN_NO_HOUSEHOLDS":
        return jsonify({ "households": []})
    elif token == "XXX_TOKEN_ONE_HOUSEHOLD":
        if householdId == "XXX_HOUSEHOLD_ONE_1":
            return jsonify({
                "players": [
                    {
                        "id": "RINCON_10001",
                        "name": "Wohnzimmer",
                        "capabilities": [
                            "AIRPLAY",
                            "AUDIO_CLIP",
                            "CLOUD",
                        ]
                    }
                ]
            })
        else:
            return jsonify({"errorCode": "ERROR_RESOURCE_GONE"}, 410)
    elif token == "XXX_TOKEN_TWO_HOUSEHOLDS":
        if householdId == "XXX_HOUSEHOLD_TWO_1":
            return jsonify({
                "players": [
                    {
                        "id": "RINCON_10001",
                        "name": "Wohnzimmer",
                        "capabilities": [
                            "AIRPLAY",
                            "AUDIO_CLIP",
                            "CLOUD",
                        ]
                    }
                ]
            })
        elif householdId == "XXX_HOUSEHOLD_TWO_2":
            return jsonify({
                "players": [
                    {
                        "id": "RINCON_10021",
                        "name": "Lounge",
                        "capabilities": [
                            "AIRPLAY",
                            "CLOUD",
                        ]
                    },
                    {
                        "id": "RINCON_10022",
                        "name": "Badezimmer",
                        "capabilities": [
                            "AIRPLAY",
                            "AUDIO_CLIP",
                            "CLOUD",
                        ]
                    }
                ]
            })
        else:
            return jsonify({"errorCode": "ERROR_RESOURCE_GONE"}, 410)
    elif token == "XXX_TOKEN_MANY_HOUSEHOLDS":
        for i in range(1, 5 + 1):
            if householdId == "XXX_HOUSEHOLD_MANY_{0}".format(i):
                return jsonify({
                    "players": [{
                            "id": "RINCON_1000{0}".format(x),
                            "name": "Player {0} in Household {1}".format(x, i),
                            "capabilities": [
                                "AIRPLAY",
                                "AUDIO_CLIP" if x % 2 == 0 else "EMPTY",
                                "CLOUD",
                            ]
                        } for x in range(1, (i * 2) + 1)]
                    })
        return jsonify({"errorCode": "ERROR_RESOURCE_GONE"}, 410)
    else:
        return make_response('Invalid access_token', 401)

'''
https://api.ws.sonos.com/control/api/v1/households
    headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
'''
@app.route("/control/api/v1/households", methods=["GET"])
def control_api_v1_houesholds():
    token = get_bearer_token(request.headers['Authorization'])
    if token == "XXX_TOKEN_NO_HOUSEHOLDS":
        return jsonify({ "households": []})
    elif token == "XXX_TOKEN_ONE_HOUSEHOLD":
        return jsonify({
            "households": [
                    {
                        "id": "XXX_HOUSEHOLD_ONE_1",
                    }
                ]})
    elif token == "XXX_TOKEN_TWO_HOUSEHOLDS":
        return jsonify({
            "households": [
                    {
                        "id": "XXX_HOUSEHOLD_TWO_1",
                    },
                    {
                        "id": "XXX_HOUSEHOLD_TWO_2",
                    },
                ]})
    elif token == "XXX_TOKEN_MANY_HOUSEHOLDS":
        return jsonify({
            "households": [
                    {
                        "id": "XXX_HOUSEHOLD_MANY_1",
                    },
                    {
                        "id": "XXX_HOUSEHOLD_MANY_2",
                    },
                    {
                        "id": "XXX_HOUSEHOLD_MANY_3",
                    },
                    {
                        "id": "XXX_HOUSEHOLD_MANY_4",
                    },
                    {
                        "id": "XXX_HOUSEHOLD_MANY_5",
                    },
                ]})
    else:
        return make_response('Invalid access_token', 401)

def check_auth(header, username, password):
    print(header)
    if header.startswith('Basic '):
        encoded_creds = header[len('Basic '):]
        print(encoded_creds)
        decoded_creds = b64decode(encoded_creds)
        print(decoded_creds)
        return decoded_creds == '{0}:{1}'.format(username, password).encode('ASCII')
    else:
        return False

'''
http://localhost:5001/login/v3/oauth?client_id=XXX_SONOS_APPKEY&response_type=code&state=CRYPTICSTATE==&scope=playback-control-all&redirect_uri=http://localhost:5001/sonos_auth
'''
@app.route("/login/v3/oauth", methods=['GET'])
def login_v3_oauth():
    args = request.args
    if 'client_id' in args and 'response_type' in args and args['response_type'] == 'code' and 'state' in args and 'scope' in args and 'redirect_uri' in args:
        if args['client_id'] != "XXX_SONOS_APPKEY":
            return make_response('Invalid client_id', 400)
        elif args['scope'] != 'playback-control-all':
            return make_response('Invalid scope', 400)
        elif not args['redirect_uri'].startswith('http://localhost'):
            return make_response('Invalid redirect_uri', 400)
        else:
            return redirect('{0}?code={1}&state={2}'.format(args['redirect_uri'], 'XXX_AUTH_CODE', args['state']))
    else:
        return make_response('Invalid request', 400)

@app.route("/login/v3/oauth/access", methods=['POST'])
def login_v3_oauth_access():
    r = request.form
    if not 'grant_type' in r:
        return make_response('Invalid request', 400)

    auth = request.headers['Authorization']
    if not check_auth(auth, 'XXX_SONOS_APPKEY', 'XXX_SONOS_SECRET'):
        return make_response('Wrong username/password', 401)
    else:
        if r['grant_type'] == 'authorization_code':
            if 'code' and 'redirect_uri':
                if r['code'] != "XXX_AUTH_CODE":
                    return make_response('Invalid code', 400)
                if not r['redirect_uri'].startswith("http://localhost"):
                    return make_response('Invalid redirect_uri', 400)
                else:
                    return jsonify({
                        'access_token': 'XXX_TOKEN_TWO_HOUSEHOLDS',
                        'refresh_token': 'XXX_REFRESH_TOKEN',
                        'scope': 'playback-control-all',
                        'expires_in': 300
                    })
            else:
                return make_response('Missing code or redirect_uri for request with grant_type "authorization_code"', 400)
        elif r['grant_type'] == 'refresh_token':
            if not 'refresh_token' in r:
                return make_response('Missing refresh_token for request with grant_type "refresh_token"', 400)
            else:
                if r['refresh_token'] == 'XXX_REFRESH_TOKEN':
                    return jsonify({
                            'access_code': 'XXX_REFRESHED_ACCESS_CODE',
                            'refresh_token': 'XXX_REFRESH_TOKEN'
                        })
                else:
                    return make_response('Invalid refresh_token', 400)
        else:
            return make_response('Invalid grant_type', 400)

