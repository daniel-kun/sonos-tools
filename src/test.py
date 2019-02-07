import unittest
import os
import db
import json
import text_to_speech as tts
import filetype
import subprocess
import pymongo
import service
import uuid
from playsound import playsound


SONOSTOOLS_GCP_API_KEY = os.environ['SONOSTOOLS_GCP_API_KEY']
SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']
SONOSTOOLS_SONOSAPI_PLAYERID = os.environ['SONOSTOOLS_SONOSAPI_PLAYERID']

def get_mime_type(byteBuffer):
    (out, err) = subprocess.Popen(['file', '-b', '--mime-type', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate(byteBuffer)
    return out.decode('utf-8').strip()

class TestSonosToolsSystem(unittest.TestCase):
    def test_start_service(self):
        return
        client = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
        service.startService(client, SONOSTOOLS_GCP_API_KEY, SONOSTOOLS_SONOSAPI_PLAYERID, 8090)

    def test_Db_apikey(self):
        client = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
        result = db.find_apikey(client, "XXX")
        self.assertEqual("XXX", result['apiKey'])
        newAccessToken = str(uuid.uuid4())
        newRefreshToken = str(uuid.uuid4())
        db.update_apikey(client, "XXX", newAccessToken, newRefreshToken)
        result = db.find_apikey(client, "XXX")
        self.assertEqual(newAccessToken, result['sonosAccessToken'])
        self.assertEqual(newRefreshToken, result['sonosRefreshToken'])

    def test_Db_roundtrip(self):
        return
        client = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
        self.assertIsInstance(db.create_indexes(client), str)
        db.remove_audio(client, "XXX_TEST_ABC")
        self.assertIsInstance(db.insert_audio(client, "XXX_TEST_ABC", b"ABCD"), pymongo.results.InsertOneResult)
        self.assertEqual(db.find_audio(client, "XXX_TEST_ABC").decode('utf-8'), "ABCD")
        db.remove_audio(client, "XXX_TEST_ABC")

    def test_service(self):
        return
        # Arrange: Connect to DB, get the hash of the audio-config that should be returned, and remove the entry if it already exists:
        client = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
        expectedAudioConfigHash = tts.textToAudioConfigHash("de-DE", "Die Waschmaschine ist fertig!")
        db.remove_audio(client, expectedAudioConfigHash)
        # Act: Execute getTextToSpeechHash to synthesize the text and store the resulting mp3 in the database with the audioConfigHash as the key
        (actualAudioConfigHash, readFromCache) = service.getTextToSpeechHash(client, "de-DE", "Die Waschmaschine ist fertig!", SONOSTOOLS_GCP_API_KEY)
        # Assert: The audioConfigHashes equal, the file is stored in the database and the stored file is an MP3
        self.assertEqual(expectedAudioConfigHash, actualAudioConfigHash)
        self.assertEqual(readFromCache, False)
        audioFile = service.getAudioFileFromAudioConfigHash(client, actualAudioConfigHash)
        self.assertEqual("audio/mpeg", get_mime_type(audioFile))
        # Act 2: Now synthesize again, should be read from cache now:
        (actualAudioConfigHash, readFromCache) = service.getTextToSpeechHash(client, "de-DE", "Die Waschmaschine ist fertig!", SONOSTOOLS_GCP_API_KEY)
        # Assert 2: Now synthesize again, should be read from cache now:
        self.assertEqual(expectedAudioConfigHash, actualAudioConfigHash)
        self.assertEqual(readFromCache, True)
        #db.remove_audio(client, actualAudioConfigHash)


    def test_Speech(self):
        return
        result = tts.textToSpeech("de-DE", "Die Waschmaschine ist fertig!", SONOSTOOLS_GCP_API_KEY)
        self.assertIsNotNone(result[0])
        self.assertEqual("audio/mpeg", get_mime_type(result[1]))

    def test_Speech_Unicode(self):
        return
        result = tts.textToSpeech("de-DE", "So ein Ärgernis! 木", SONOSTOOLS_GCP_API_KEY)
        self.assertIsNotNone(result[0])
        self.assertEqual("audio/mpeg", get_mime_type(result[1]))

if __name__ == '__main__':
    unittest.main()

