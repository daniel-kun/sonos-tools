from datetime import datetime
import unittest
import os

from bson import ObjectId

import account
import sonos
import db

SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']

class TestSonosToolsFrontendSystem(unittest.TestCase):
    def test_find_account_by_google_user_id(self):
        return
        acc = account.find_account_by_google_user_id({
                'sub': 'XXX-FOOBAR',
                'email': 'd.albuschat@gmail.com',
                'name': 'Daniel Albuschat',
                'picture': 'https://www.google.de/'
                })
        self.assertEqual(False, '_id' in acc)
        self.assertEqual(False, 'userid' in acc)
        self.assertEqual('d.albuschat@gmail.com', acc['email'])
        self.assertEqual('Daniel Albuschat', acc['name'])
        self.assertEqual('https://www.google.de/', acc['picture'])
        self.assertEqual(True, 'accountid' in acc)
        self.assertEqual(str, type(acc['accountid']))
        self.assertEqual(True, 'sonosApiAppKey' in acc)
        self.assertEqual(str, type(acc['sonosApiAppKey']))
        self.assertEqual(True, 'redirectUriRoot' in acc)
        self.assertEqual(str, type(acc['redirectUriRoot']))

    def test_update_account_sonos_tokens(self):
        return
        xxxFoobarObjectId = '5c5ebcc56409600b754a7200'
        dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
        accountsCollection = dbClient['sonos-tools']['accounts']
        accountsCollection.update_one({'_id': ObjectId(xxxFoobarObjectId)}, { "$unset": { "sonos": "" } })
        accountDoc = db.find_account_id(dbClient, xxxFoobarObjectId)
        self.assertEqual(False, 'sonos' in accountDoc)

        expires = datetime.now()
        # Trim microseconds, since the resolution is not high enough when travelling through mongodb and back:
        expires = datetime(year=expires.year, month=expires.month, day=expires.day, hour=expires.hour, minute=expires.minute, second=expires.second)
        result = db.update_account_sonos_tokens(dbClient, xxxFoobarObjectId, { "access_token": "AT", "refresh_token": "RT", "scope": "playback-all", "expires_at":  expires })

        self.assertEqual(1, result.matched_count)
        self.assertEqual(1, result.modified_count)
        accountDoc = db.find_account_id(dbClient, xxxFoobarObjectId)
        self.assertEqual(True, 'sonos' in accountDoc)
        self.assertEqual("AT", accountDoc['sonos']['access_token'])
        self.assertEqual("RT", accountDoc['sonos']['refresh_token'])
        self.assertEqual("playback-all", accountDoc['sonos']['scope'])
        self.assertEqual(expires, accountDoc['sonos']['expires_at'])

    def test_sonosListPlayers(self):
        return
        dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)
        sonos.sonosListPlayers(db.find_account_id(dbClient, '5c5ebe776409600b661ebc32'))


    def test_sonosMergePlayerApiKeys_emptyAccount(self):
        account = {
            "sonos": {
            }
        }
        playerIds = ["PLAYER_0", "PLAYER_1", "PLAYER_2"]
        result = sonos.sonosMergePlayerApiKeys(account, playerIds)
        print(result)
        self.assertEqual(3, len(result))
        self.assertEqual("PLAYER_0", result[0]["playerId"])
        self.assertEqual(str, type(result[0]["apiKey"]))
        self.assertEqual("PLAYER_1", result[1]["playerId"])
        self.assertEqual(str, type(result[1]["apiKey"]))
        self.assertEqual("PLAYER_2", result[2]["playerId"])
        self.assertEqual(str, type(result[2]["apiKey"]))

    def test_sonosMergePlayerApiKeys_newPlayer(self):
        account = {
            "sonos": {
                "players": [
                    { "playerId": "PLAYER_0", "apiKey": "APIKEY_0" }
                ]
            }
        }
        playerIds = ["PLAYER_0", "PLAYER_1"]
        result = sonos.sonosMergePlayerApiKeys(account, playerIds)
        print(result)
        self.assertEqual(2, len(result))
        self.assertEqual("PLAYER_0", result[0]["playerId"])
        self.assertEqual("APIKEY_0", result[0]["apiKey"])
        self.assertEqual("PLAYER_1", result[1]["playerId"])
        self.assertEqual(str, type(result[1]["apiKey"]))
        self.assertNotEqual("APIKEY_9", result[1]["apiKey"])

    def test_sonosMergePlayerApiKeys_deletedPlayer(self):
        account = {
            "sonos": {
                "players": [
                    { "playerId": "PLAYER_0", "apiKey": "APIKEY_0" },
                    { "playerId": "PLAYER_1", "apiKey": "APIKEY_1" },
                ]
            }
        }
        playerIds = ["PLAYER_0"]
        result = sonos.sonosMergePlayerApiKeys(account, playerIds)
        print(result)
        self.assertEqual(1, len(result))
        self.assertEqual("PLAYER_0", result[0]["playerId"])
        self.assertEqual("APIKEY_0", result[0]["apiKey"])

    def test_sonosMergePlayerApiKeys_addedAnddeletedPlayer(self):
        account = {
            "sonos": {
                "players": [
                    { "playerId": "PLAYER_0", "apiKey": "APIKEY_0" },
                    { "playerId": "PLAYER_1", "apiKey": "APIKEY_1" },
                ]
            }
        }
        playerIds = ["PLAYER_0", "PLAYER_2"]
        result = sonos.sonosMergePlayerApiKeys(account, playerIds)
        self.assertEqual(2, len(result))
        self.assertEqual("PLAYER_0", result[0]["playerId"])
        self.assertEqual("APIKEY_0", result[0]["apiKey"])
        self.assertEqual("PLAYER_2", result[1]["playerId"])
        self.assertEqual(str, type(result[1]["apiKey"]))

if __name__ == '__main__':
    unittest.main()

