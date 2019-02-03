import os
import db
import tts
from playsound import playsound


SONOSTOOLS_GCP_API_KEY = os.environ['SONOSTOOLS_GCP_API_KEY']
SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']

def testDb():
    client = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
    print(db.find_audio(client, "ABCD"))

def testSpeech():
    halloFileName = "hallo.mp3"
    try:
        f = open(halloFileName, "wb")
        f.write(tts.textToSpeech("de-DE", "Die Waschmaschine ist fertig!", SONOSTOOLS_GCP_API_KEY))
        f.close()
        playsound(halloFileName)
    except:
        os.remove(halloFileName)
        raise

testDb()
testSpeech()

