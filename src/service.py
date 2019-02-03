import db
import json
from functools import partial
import text_to_speech as tts
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler

# Result: [0] = audioConfigHash, [1] = True when read from cache, False when synthesize was required
def getTextToSpeechHash(client, languageCode, text, apiKey):
    audioConfigHash = tts.textToAudioConfigHash(languageCode, text)
    audio = db.find_audio(client, audioConfigHash)
    if audio == None:
        (audioConfigHash, audioFile) = tts.textToSpeech(languageCode, text, apiKey)
        db.insert_audio(client, audioConfigHash, audioFile)
        return (audioConfigHash, False)
    else:
        return (audioConfigHash, True)

def getAudioFileFromAudioConfigHash(client, audioConfigHash):
    return db.find_audio(client, audioConfigHash)

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, dbClient, googleApiKey, sonosPlayerId, *args, **kwargs):
        self.dbClient = dbClient
        self.googleApiKey = googleApiKey
        self.sonosPlayerId = sonosPlayerId
        super().__init__(*args, **kwargs)

    def serveAudioFile(self, audioConfigHash):
        audioFile = getAudioFileFromAudioConfigHash(self.dbClient, audioConfigHash)
        if audioFile != None:
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.end_headers()
            self.wfile.write(audioFile)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('<html><body><h1>Could not find this audio file</h1>\n'.encode('utf-8'))

    def do_GET(self):
        # TODO: Read audioFile from DB and return file
        audioFilePrefix = '/static/audioFile/'
        sonosAuthPrefix = '/sonos_auth/'
        print(self.path)
        if self.path.startswith(audioFilePrefix):
            audioConfigHash = self.path[len(audioFilePrefix):]
            return self.serveAudioFile(audioConfigHash)
        elif self.path.startswith(sonosAuthPrefix):
            raise Exception("Not implemented, yet")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write('<html><body><h1>Not found</h1>\n'.encode('utf-8'))

    def execSonos(self, apiKey, sonosAccessToken, sonosRefreshToken, sonosPlayerId, audioConfigHash):
        headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
        body = {
            "name": "Demo Clip",
            "appId": "com.acme.com",
            "streamUrl": "http://hr8jeljvudseiccl8kzrps.webrelay.io/static/audioFile/{0}".format(audioConfigHash)
        }
        request = requests.post("https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip".format(sonosPlayerId),
                headers=headers,
                json=body)
        if request.status_code == 401:
            print("Sonos API token not valid, trying to refresh")
            headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
            refreshRequest = requests.post("https://api.sonos.com/login/v3/oauth/access", headers=headers, data={
                "grant_type": "refresh_token",
                "refresh_token": sonosRefreshToken
            })
            if refreshRequest.status_code != 200:
                print(sonosRefreshToken)
                print(refreshRequest)
                raise Exception("Sonos API Access Token invalid and could not be refreshed.")
            sonosAccessToken = refreshRequest['access_token']
            sonosRefreshToken = refreshRequest['refresh_token']
            db.update_apikey(self.dbClient, apiKey, sonosAccessToken, sonosRefreshToken)
            headers = { "Authorization": "Bearer {0}".format(sonosAccessToken) }
            print("Refreshed Sonos API token")
            return requests.post("https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip".format(sonosPlayerId),
                    headers=headers,
                    json=body)
            pass
        return request

    def do_POST(self):
        body = self.rfile.read(int(self.headers['content-length']))
        try:
            request = json.loads(body)
            if not ('key' in request and 'text' in request and 'languageCode' in request):
                raise Exception('Fields "key", "languageCode" and "text" must be included in the request')

            apiKeyDoc = db.find_apikey(self.dbClient, request['key'])
            if apiKeyDoc == None:
                raise Exception('Invalid "key"')

            (audioConfigHash, fromCache) = getTextToSpeechHash(self.dbClient, request['languageCode'], request['text'], self.googleApiKey)
            result = self.execSonos(request['key'], apiKeyDoc['sonosAccessToken'], apiKeyDoc['sonosRefreshToken'], self.sonosPlayerId, audioConfigHash)
            if result.status_code == 200:
                self.send_response(200)
                self.end_headers()
                if fromCache:
                    self.wfile.write("Roger, playing sound (from cache)".encode('utf-8'))
                else:
                    self.wfile.write("Roger, playing sound (synthesized just for you!)".encode('utf-8'))
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write("Failed to play sound")
        except Exception as err:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(json.dumps({
                    "error": str(err)
                }).encode('utf-8'))


def startService(mongoDbClient, googleApiKey, playerId, port):
    try:
        handler = partial(RequestHandler, mongoDbClient, googleApiKey, playerId)
        server = HTTPServer(('', port), handler)
        print("Starting server on port {0}...".format(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()

