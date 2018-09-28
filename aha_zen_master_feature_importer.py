import requests
import config
import os
import json
from objectifier import Objectifier
import github3
from autologging import logged,traced,TRACE 
import logging
import sys
from datetime import datetime

logging.basicConfig(level=logging.INFO, stream=sys.stderr,format="%(levelname)s:%(filename)s,%(lineno)d:%(name)s.%(funcName)s:%(message)s",filename=str(datetime.now()).replace(':','_').replace('.','_')+'.log', filemode='w')




AHA_TOKEN=os.environ.get('AHA_TOKEN')
ZENHUB_TOKEN=os.environ.get('ZENHUB_TOKEN')
GITHUB_TOKEN=os.environ.get('GITHUB_TOKEN')



AHA_HEADER={'Authorization':AHA_TOKEN,'Content-Type': "application/json","User-Agent":"praveentechnic@gmail.com"}
ZENHUB_HEADER={'X-Authentication-Token':ZENHUB_TOKEN}




########################DATA_STORE##################################
ENDURANCE= requests.get('https://ndurance.herokuapp.com/api/data_store/aha_zen', headers={'x-api-key':config.ndurance_key}).json()
############################################################

#Get list of Epics from Zen hub
def getListOfEpicsZen():
    rs=requests.get(url='https://api.zenhub.io/p1/repositories/{0}/epics'.format(config.Zenhub_repo_Id),headers=ZENHUB_HEADER)
    if(rs.status_code==200):
        return rs.json()
    else:
        logging.error("Failure While Fetching details from Zenhub"+ str(rs.status_code)+ str(rs.content))
        return None

#Get Translation data - handle key errors internally
def getTranslationData(jsoncontent,key):
    try:
        return jsoncontent[key]
    except KeyError:
        
        return None

#create an instance of github_object and return the same
def github_object(TOKEN,repository):
    repository=repository
    gh = github3.GitHub(token=TOKEN)
    owner,name=repository.split('/',1)
    repo= gh.repository(owner,name)
    return repo

#Get Details of an issue from Zenhub
def getIssueDetailFromZen(repoid,issue_id):
    rs= requests.get('https://api.zenhub.io/p1/repositories/{0}/issues/{1}'.format(str(repoid),str(issue_id)),headers=ZENHUB_HEADER)
    if(rs.status_code==200):
        result= rs.json()
        result['id']=issue_id
        return result
    else:
        #Log error
        return None

# Get list of available release milestones from Aha
def getAllReleasesfromAha():
    current_page=1
    totalpage=10
    releases={}
    while current_page<=totalpage:
        rs=requests.get('https://qube-cinema.aha.io/api/v1/products/{0}/releases'.format(config.product_ref),headers=AHA_HEADER)
        data=rs.json()
        for items in data['releases']:
            releases[items['name']]=items
        totalpage=data['pagination']['total_pages']
        current_page=current_page+1
    return releases

def getEpicDataGit():
    pass

#Get all the master features from Aha
def getMasterFeatureAha():
    rs=requests.get(url='https://qube-cinema.aha.io/api/v1/master_features', headers=AHA_HEADER)
    if(rs.status_code==200):
        return rs.json()
    else:
        #add Failure Logs
        return None

#Create a new master feature on Aha
def insertMasterFeatureAha(release_id,NAME,DESC,STATUS="Under consideration"):    
    model={
  "master_feature": {
    "name": NAME,
    "description": DESC,    
    "workflow_status": {            
            "name": STATUS
        }
            }
            }
    if(release_id != None):
        rs=requests.post(url='https://qube-cinema.aha.io/api/v1/releases/{release_id}/master_features'.format(release_id=release_id),data=json.dumps(model), headers=AHA_HEADER)
        return rs
    else:
        rs=requests.post(url='https://qube-cinema.aha.io/api/v1/products/{0}/master_features'.format(config.product_id),data=json.dumps(model),headers=AHA_HEADER)
        return rs


#Update the Master feature on Aha
def updateMasterFeatureAha(id,changes={}):
    model={
  "master_feature": {}
    }
    for items in changes:
        model['master_feature'][items]=changes[items]
    rs=requests.put(url='https://qube-cinema.aha.io/api/v1/master_features/{0}'.format(id), data=json.dumps(model), headers=AHA_HEADER)
    return rs

#Get details about the master feature on Aha
def getMasterFeatureDetailAha(id):
    rs=requests.get('https://qube-cinema.aha.io/api/v1/master_features/{0}'.format(id), headers=AHA_HEADER)
    if(rs.status_code==200):
        return rs.json()
    else:
        #TODO: Log Failure Error for incorrect response
        return None

#Main workflow
def main():
    Aha_releases= getAllReleasesfromAha()
    Zen_Epics=getListOfEpicsZen()
    git_repo=github_object(GITHUB_TOKEN,config.repo_name)
    for items in Zen_Epics['epic_issues']:
        #check if item is available in Endurance:
        print 'processing: '+str(items)
        aha_epic=getTranslationData(ENDURANCE,str(items['issue_number']))
        if(aha_epic==None):
            issue=git_repo.issue(items['issue_number'])
            
            release_id=Aha_releases[issue.milestone.title]['reference_num'] if issue.milestone is not None else None
            zen_issue_detail=getIssueDetailFromZen(repoid=config.Zenhub_repo_Id,issue_id=items['issue_number'])
            name=issue.title
            description=issue.body
            status=getTranslationData(json.load(open('zen2ahaMap.json')),zen_issue_detail['pipeline']['name'])            
            if(status is not None):
                response=insertMasterFeatureAha(release_id,name,description,status)
                if(response.status_code==200):
                    this_master_feature=response.json()
                    logging.info("Successfully created:  "+  str(this_master_feature['master_feature']['reference_num']))
                    ENDURANCE[str(items['issue_number'])]={
                        "aha_ref_num":this_master_feature['master_feature']['reference_num']
                    }
                else:
                    #TODO log Error Failure
                    print response.status_code
            else:
                #TODO Log error for status not available
                print ' status un available'
                pass
        else:
            #TODO Logic for updating the Master feature
            #Update the folllowing> name, description, status, release id
            issue=git_repo.issue(items['issue_number'])
            zen_issue_detail=getIssueDetailFromZen(repoid=config.Zenhub_repo_Id,issue_id=items['issue_number'])
            changes={}
            G_name=issue.title
            G_description=issue.body
            Z_status=getTranslationData(json.load(open('zen2ahaMap.json')),zen_issue_detail['pipeline']['name'])            
            G_Release=issue.milestone.title if issue.milestone is not None else None
            Aha_MF=getMasterFeatureDetailAha(aha_epic['aha_ref_num'])        
            if(Aha_MF is not None):
                Aha_MF=Aha_MF['master_feature']
                A_name=Aha_MF['name']
                A_description=Aha_MF['description']['body']
                A_status=Aha_MF['workflow_status']['name']
                A_release_id=Aha_MF['release']['reference_num']
                if(A_name!=G_name):
                    changes['name']=G_name
                if(A_description!=G_description):
                    changes['description']=G_description
                if(A_status!=Z_status):
                    changes['workflow_status']={'name':Z_status}
                if(G_Release !=None):
                    if(A_release_id!=Aha_releases[G_Release]['reference_num']):
                        changes['release']={'reference_num':Aha_releases[G_Release]['reference_num']}
                if(changes!={}):
                    update_response=updateMasterFeatureAha(aha_epic['aha_ref_num'],changes=changes)
                    if(update_response.status_code==200):
                        #TODO: Print update log
                        print "updated!:  "+ str(aha_epic) + str(changes)
                    else:
                        #TODO: Log Error
                        pass
    #FBC.getdb().child('ENDURANCE').set(ENDURANCE)
    update_to_endurance=requests.post('https://ndurance.herokuapp.com/api/data_store/aha_zen',headers={'x-api-key':config.ndurance_key,'Content-Type':'application/json'}, data= json.dumps(ENDURANCE))
    if(update_to_endurance.status_code==201):
        logging.info("successfully updated status to endurance")
    else:
        logging.error("Non 200 code from ndurance"+str(update_to_endurance.status_code))
    

main()
