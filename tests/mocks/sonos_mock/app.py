from flask import Flask
from flask import make_response
from flask import request
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


https://api.sonos.com/login/v3/oauth/access
    headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
    {
        "grant_type": "refresh_token",
        "refresh_token": sonosRefreshToken
    }
    ///
    auth=(SONOSTOOLS_SONOSAPI_APPKEY, SONOSTOOLS_SONOSAPI_SECRET)
    {
        "grant_type": "authorization_code",
        "code": sonosAuthCode,
        "redirect_uri": '{0}/sonos_auth'.format(SONOSTOOLS_REDIRECT_ROOT)
    }

https://api.ws.sonos.com/control/api/v1/households
    headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }

https://api.ws.sonos.com/control/api/v1/households/{0}/groups
    headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
'''

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

@app.route("/login/v3/oauth/access", methods=['POST'])
def login_v3_oauth_access():
    # TODO:
    '''
    https://api.sonos.com/login/v3/oauth/access
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
        {
            "grant_type": "refresh_token",
            "refresh_token": sonosRefreshToken
        }
        ///
    '''
    r = request.form
    if not 'grant_type' in r:
        return make_response('Invalid request', 400)

    if r['grant_type'] == 'authorization_code':
        auth = request.headers['Authorization']
        if not check_auth(auth, 'FAKE_SONOSAPI_APPKEY', 'FAKE_SONOSAPI_SECRET'):
            return make_response('Wrong username/password'.format(auth), 403)
        else:
            return jsonify({
                'access_code': 'XXX_INITIAL_ACCESS_CODE',
                'refresh_token': 'XXX_REFRESH_TOKEN',
                'scope': 'playback-control-all',
                'expires_in': 300
            })
    elif r['grant_type'] == 'refresh_token':
        return make_response('Not implemented (refresh_token)', 404)
    else:
        return make_response('Invalid grant_type', 400)


