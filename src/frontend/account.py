import db
import os

SONOSTOOLS_SONOSAPI_APPKEY = os.environ['SONOSTOOLS_SONOSAPI_APPKEY']
SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']
SONOSTOOLS_REDIRECT_ROOT = os.environ['SONOSTOOLS_REDIRECT_ROOT']

def find_account_by_google_user_id(idinfo):
    userid = idinfo['sub']
    account = db.find_account(dbClient, userid)
    if account == None:
        # First login for this google user, create an account:
        account = {
            'auth_type': 'Google',
            'userid': userid,
            'email': idinfo['email'],
            'name': idinfo['name'],
            'picture': idinfo['picture'],
            'sonosApiAppKey': SONOSTOOLS_SONOSAPI_APPKEY
        }
        accountid = db.insert_account(dbClient, account).inserted_id
        account['accountid'] = str(accountid)
    else:
        account['accountid'] = str(account['_id'])

    del account['userid']
    if '_id' in account:
        del account['_id']
    account['redirectUriRoot'] = SONOSTOOLS_REDIRECT_ROOT
    return account

dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)

