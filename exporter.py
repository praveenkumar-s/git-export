import github3
import csv
import requests
import sys
import argparse
import os
import progressbar
reload(sys)
sys.setdefaultencoding('utf-8')

try:
    GITHUB_TOKEN=os.environ.get('GITHUB_TOKEN')
    ZENHUB_TOKEN=os.environ.get('ZENHUB_TOKEN')
except:
    print "No Token Found. Use export GITHUB_TOKEN=<personal access token from github> \n export ZENHUB_TOKEN=<personal access token from zenhub>"
    sys.exit()



def getZenhub_estimate(repoId,IssueNumber):
    rs=requests.get(url='https://api.zenhub.io/p1/repositories/{0}/issues/{1}'.format(repoId,str(IssueNumber)), headers={'X-Authentication-Token':ZENHUB_TOKEN})    
    if(rs.status_code==200):
        return rs.json()
    else:
        return None

def collate_labels(label_Array):
    label_data=""
    for label in label_Array:
        label_data=label.name+' | '
    return label_data

def write_to_csv(filename,data):
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def arg_parser():
    args = argparse.ArgumentParser(
        description='Export Issues from Github to csv'
    )
    args.add_argument(
        '--repo',
        help='Repository to retrieve issues from (e.g. praveenkumar-s/rpc-openstack). ',
         dest='repository', required=True, default=[],
    )

    args.add_argument(
        '--filename',
        help='Name of the outputfile. Eg: git-export.csv ',
         dest='filename', required=True, default=[],
    )

    return args

def main(repository, file_name):
    gh = github3.GitHub(token=GITHUB_TOKEN)
    owner,name=repository.split('/',1)
    repo= gh.repository(owner,name)
    repoId=repo.id
    data=[['ID','Link','Title','Status','Milestone','Assignee','CreatedOn','Estimate','Labels']]
    
    with progressbar.ProgressBar(max_value=progressbar.UnknownLength) as bar:
        for items in repo.issues():
            row=[]
            issuenumber=items.number
            row.append(str(issuenumber))
            row.append(str(items.html_url))
            row.append(str(items.title))
            row.append(str(items.state))
            row.append(str(items.milestone))
            row.append(str(items.assignee.login))
            row.append(str(items.created_at.strftime('%m/%d/%Y')))
            try:
                estimate=getZenhub_estimate(repoId,issuenumber)['estimate']['value']
            except:
                estimate=0
            row.append(estimate)
            row.append(collate_labels(items.original_labels))
            data.append(row)
            
            bar.update()
    write_to_csv(file_name,data)
    


