import pyrebase
import sys
import os

class Firebase_client:
    def __init__(self):        
        config = {
    'apiKey': os.environ['FIREBASE_API_KEY'],
    'authDomain': os.environ['FIREBASE_AUTH_DOMAIN'],
    'databaseURL': os.environ['FIREBASE_DATABASE_URL'],
    'serviceAccount': {
        # Your "Service account ID," which looks like an email address.
        'client_email': os.environ['FIREBASE_CLIENT_EMAIL'], 
        # The part of your Firebase database URL before `firebaseio.com`. 
        # e.g. `fiery-flames-1234`
        'client_id': os.environ['FIREBASE_CLIENT_ID'],
        # The key itself, a long string with newlines, starting with 
        # `-----BEGIN PRIVATE KEY-----\n`
        'private_key': os.environ['FIREBASE_PRIVATE_KEY'].replace('\\n', '\n'),
        # Your service account "key ID." Mine is 40 alphanumeric characters.
        'private_key_id': os.environ['FIREBASE_PRIVATE_KEY_ID'],
        'type': 'service_account'
    },
    'storageBucket': ''
}
        self.firebase = pyrebase.initialize_app(config)
        self.firebase.auth()
    def getdb(self):
        return self.firebase.database()

    def putvalue(self, child, data):
        db= self.firebase.database()
        db.child(child).set(data)
    def getdata(self,tag):
        db= self.firebase.database()
        try:
            return db.child(tag).get().val()
        except:
            return None