import pyrebase
import sys


class Firebase_Client:
    def __init__(self):        
        config = {
        "apiKey": "AIzaSyBEkyCiKYgcHhxctsgTba04z1Xiq1DGpP0",
        "authDomain": "releasetrackerqube.firebaseapp.com",
        "databaseURL": "https://releasetrackerqube.firebaseio.com/",
        "storageBucket": "releasetrackerqube.appspot.com",
        "serviceAccount": "sa.json"
        }
        self.firebase = pyrebase.initialize_app(config)
        self.firebase.auth()
    def getdb(self):
        return self.firebase.database()

    def putvalue(self, child, data):
        db= self.firebase.database()
        db.child(child).set(data)


