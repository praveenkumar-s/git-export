import requests
import sys
import json
reload(sys)
from autologging import logged,traced,TRACE 
import logging
import time
from objectifier import Objectifier
import os
import argparse
from firebase_client import Firebase_Client 
from datetime import datetime
import config

logging.basicConfig(level=logging.INFO, stream=sys.stderr,format="%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s", filename=str(datetime.now())+'.log', filemode='w')
sys.setdefaultencoding('utf-8')

AHA_TOKEN=os.environ.get('AHA_TOKEN')
ZENHUB_TOKEN=os.environ.get('ZENHUB_TOKEN')
AHA_HEADER={'Authorization':AHA_TOKEN,'Content-Type': "application/json","User-Agent":"praveentechnic@gmail.com"}
ZENHUB_HEADER={'X-Authentication-Token':ZENHUB_TOKEN}
map_data= json.load(open('zen2ahaMap.json'))

########################DATA_STORE##################################
FBC=Firebase_Client()
ENDURANCE= dict(FBC.getdb().child('ENDURANCE').get().val())

############################################################


#Get all the features along with their Ids and referencenumbers
def getFeatureListFromAha():
    features=[] 
    total_page=9
    current_page=1
    
    while current_page<=total_page:
        rs= requests.get('https://qube-cinema.aha.io/api/v1/features', params={'page':current_page} ,headers=AHA_HEADER)
        if(rs.status_code==200):
            feature_set=rs.json()
            for items in feature_set['features']:
                features.append(items)
            current_page=feature_set['pagination']['current_page'] + 1
            total_page=feature_set['pagination']['total_pages']
        else:
            logging.error('Non 200 error code thrown '+ str(rs.status_code))
            #handle failures

    return features

#Get Translation data
def getTranslationData(jsoncontent,key):
    try:
        return jsoncontent[key]
    except KeyError:
        logging.error("The requested translation data {0} is not found on the map".format(key))
        return None


#Get Details of a given feature
def getFeatureDetailFromAha(reference_num):
    rs= requests.get('https://qube-cinema.aha.io/api/v1/features/'+reference_num , headers=AHA_HEADER)
    if(rs.status_code==200):
        return rs.json()['feature']
    elif(rs.status_code==429):
        #Handle Ratelimits
        time.sleep(10)
        return getFeatureDetailFromAha(reference_num)
    else:
        return None


#Get Details for a given issue from Zen
def getIssueDetailFromZen(repoid,issue_id):
    rs= requests.get('https://api.zenhub.io/p1/repositories/{0}/issues/{1}'.format(str(repoid),str(issue_id)),headers=ZENHUB_HEADER)
    if(rs.status_code==200):
        result= rs.json()
        result['id']=issue_id
        return result
    else:
        #Log error
        return None


def getEpicDetailfromZen(repoid,epic_id):
    rs=requests.get('https://api.zenhub.io/p1/repositories/{0}/epics/{1}'.format(repoid,epic_id),headers=ZENHUB_HEADER)
    if(rs.status_code==200):
        return rs.json()
    elif(rs.staus_code==429):
        #handle ratelimit
        time.sleep(10)
        return getEpicDetailfromZen(repoid,epic_id)
    else:
        return None


def buildEpicStoryMap(repoid):
    All_Epics=None
    issue_epic_map={}
    rs=requests.get('https://api.zenhub.io/p1/repositories/{0}/epics/'.format(repoid),headers=ZENHUB_HEADER)
    if(rs.status_code==200):
        All_Epics=rs.json()
    for items in All_Epics['epic_issues']:
        epic_data=getEpicDetailfromZen(repoid,items['issue_number'])
        if(epic_data is not None):
            for issues in epic_data['issues']:
                issue_epic_map[str(issues['issue_number'])]=items['issue_number']
    return issue_epic_map

EPIC_MAP=buildEpicStoryMap(config.Zenhub_repo_Id)

#Compare status and generate diff 
def generatediff(Aha_feature,Zen_issue):
    zen=Objectifier(Zen_issue)
    Aha=Objectifier(Aha_feature)
    changes=[]
    try:        
        if(Aha.workflow_status.name != getTranslationData(map_data,zen.pipeline.name) and getTranslationData(map_data,zen.pipeline.name) is not None):
            changes.append({'workflow_status':{"name":getTranslationData(map_data,zen.pipeline.name)}})            
        if(Aha.original_estimate!=zen.estimate.value):
            changes.append({'original_estimate':zen.estimate.value}) 
        if(zen.is_epic==False):
            try:
                Aha_Epic=Aha.master_feature.reference_num
            except:
                Aha_Epic=None
            try:
                Zen_Epic=ENDURANCE[str(EPIC_MAP[zen.id])]['aha_ref_num']
            except:
                Zen_Epic=None
            if(Aha_Epic!=Zen_Epic and Zen_Epic is not None):
                changes.append({'master_feature':Zen_Epic})

    except Exception as e:
        logging.error(e.message)
    return changes

#Update details on to aha and Log the same in detail    
def update_aha(Aha_id,patchdata,skips=[], include=[]):
    update_data_schema={
        "feature":{}
    }
    if(len(patchdata)==0):
        logging.info(Aha_id+"  No Update found!")
        return 0
    elif(Aha_id not in skips):# and Aha_id=='QS-13'):
        
        for items in patchdata:
            update_data_schema['feature'].update(items)                
        rs=requests.put('https://qube-cinema.aha.io/api/v1/features/{0}'.format(Aha_id), headers=AHA_HEADER , data=json.dumps(update_data_schema))
        if(rs.status_code==200):
            logging.info(Aha_id+" "+str(update_data_schema))
            return 1
        else:
            logging.error(Aha_id+' Oops something Went wrong while updating'+ str(rs.status_code)+' '+ json.dumps(update_data_schema))
            return -1
    #REMOVE THIS
    else:
        return 0
def arg_parser():
    args = argparse.ArgumentParser(
        description='Sync Status and Estimates from Zenhub to Aha!'
    )
    args.add_argument(
        '--skip',
        help='If we want to skip syncing of few features, we can specify them in this by using the sync flag. Eg "QS-14","QS-15" ..',
         dest='skip', required=False, default=[],
    )


    return args



def main(skip=[]):
    change_log={'count':0,'errors':0,'changes':[]}
    #get feature list from aha
    FeatureList=getFeatureListFromAha()
    for items in FeatureList:
        AhaFeature=getFeatureDetailFromAha(items['reference_num'])
        compound_id=str(filter(lambda types: types['name'] == 'compound_id', AhaFeature['integration_fields'])[0]['value'])
        repoId=compound_id.split('/')[0]
        issueId=compound_id.split('/')[1]
        ZenIssue=getIssueDetailFromZen(repoId,issueId)
        diff=generatediff(AhaFeature,ZenIssue)
        state=update_aha(items['reference_num'],diff)
        if(state>0):
            change_log['count']=change_log['count']+1
        elif(state<0):
            change_log['errors']=change_log['errors']+1
        change_log['changes'].append({items['reference_num']:diff})
    logging.info(str(change_log))


if __name__ == '__main__':
    if(AHA_TOKEN==None or AHA_HEADER==None):
        logging.error("Tokens not set, set AHA_TOKEN and  AHA_HEADER as environment variables")
        sys.exit(1)
    arg=arg_parser().parse_args()
    main(arg.skip)