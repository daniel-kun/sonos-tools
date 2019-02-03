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
        db.insert(client, audioConfigHash, audioFile)
        return (audioConfigHash, False)
    else:
        return (audioConfigHash, True)

def getAudioFileFromAudioConfigHash(client, audioConfigHash):
    return db.find_audio(client, audioConfigHash)

class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, dbClient, googleApiKey, sonosAccessToken, sonosPlayerId, *args, **kwargs):
        self.dbClient = dbClient
        self.googleApiKey = googleApiKey
        self.sonosAccessToken = sonosAccessToken
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

    def do_POST(self):
        body = self.rfile.read(int(self.headers['content-length']))
        try:
            request = json.loads(body)
            if not ('key' in request and 'text' in request and 'languageCode' in request):
                raise Exception('Fields "key", "languageCode" and "text" must be included in the request')

            if request['key'] != "966e08a9-b41c-45ad-bc07-3e4bdda17579":
                raise Exception('Invalid "key"')

            (audioConfigHash, _) = getTextToSpeechHash(self.dbClient, request['languageCode'], request['text'], self.googleApiKey)
            request = requests.post("https://api.ws.sonos.com/control/api/v1/players/{0}/audioClip".format(self.sonosPlayerId),
                    headers={
                        "Authorization": "Bearer {0}".format(self.sonosAccessToken)
                    },
                    json={
                        "name": "Demo Clip",
                        "appId": "com.acme.com",
                        "streamUrl": "http://hr8jeljvudseiccl8kzrps.webrelay.io/static/audioFile/{0}".format(audioConfigHash)
                    })
            result = request.json()
            if request.status_code == 200 and "id" in result:
                self.send_response(200)
                self.end_headers()
                self.wfile.write("Roger, playing sound".encode('utf-8'))
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write("Failed to play sound")
        except Exception as err:
            self.send_response(401)
            self.end_headers()
            self.wfile.write(json.dumps({
                    "error": err.str().encode('utf-8')
                }))


def startService(mongoDbClient, googleApiKey, sonosAccessToken, playerId, port):
    try:
        handler = partial(RequestHandler, mongoDbClient, googleApiKey, sonosAccessToken, playerId)
        server = HTTPServer(('', port), handler)
        print("Starting server on port {0}...".format(port))
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()

