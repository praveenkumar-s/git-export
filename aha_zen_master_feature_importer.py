import requests
import config
import os
import json


AHA_TOKEN=os.environ.get('AHA_TOKEN')
ZENHUB_TOKEN=os.environ.get('ZENHUB_TOKEN')
AHA_HEADER={'Authorization':AHA_TOKEN,'Content-Type': "application/json","User-Agent":"praveentechnic@gmail.com"}
ZENHUB_HEADER={'X-Authentication-Token':ZENHUB_TOKEN}

# Get list if epics from Zenhub
# Get details about the epic
# Create master features on Aha!. Decide upon the features that needs to be added on to it
# Find a way to link user stories to respective epics
# Use database for communication : preferebly firebase

#get list of epics from Zen and return
def getListOfEpicsZen():
    rs=requests.get(url='https://api.zenhub.io/p1/repositories/{0}/epics'.format(config.Zenhub_repo_Id),headers=ZENHUB_HEADER)
    if(rs.status_code==200):
        return rs.json()
    else:
        #add failure Logs
        return None



def getEpicDataGit():
    pass

def getMasterFeatureAha():
    rs=requests.get(url='https://qube-cinema.aha.io/api/v1/master_features', headers=AHA_HEADER)
    if(rs.status_code==200):
        return rs.json()
    else:
        #add Failure Logs
        return None

def insertMasterFeatureAha(NAME,DESC,EST):
    
    model={
  "master_feature": {
    "name": NAME,
    "description": DESC,
    "original_estimate_text": EST
            }
            }
    rs=requests.post(url='https://qube-cinema.aha.io/api/v1/products/{product_id}/master_features'.format(product_id=config.product_id),data=json.dumps(model))

def updateMasterFeatureAha():
    pass


def updateFeaturesAha():
    pass

