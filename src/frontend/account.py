import db
import os

SONOSTOOLS_MONGODB_CONNECTURI = os.environ['SONOSTOOLS_MONGODB_CONNECTURI']

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
            'picture': idinfo['picture']
        }
        accountid = db.insert_account(dbClient, account).inserted_id
        del account['userid']
        if '_id' in account:
            del account['_id']
        account['accountid'] = str(accountid)
        return account
    else:
        del account['userid']
        account['accountid'] = str(account['_id'])
        if '_id' in account:
            del account['_id']
        return account

dbClient = db.connect(SONOSTOOLS_MONGODB_CONNECTURI)

