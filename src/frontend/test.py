import unittest
import account

class TestSonosToolsFrontendSystem(unittest.TestCase):
    def test_find_account_by_google_user_id(self):
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

if __name__ == '__main__':
    unittest.main()
