import os
import requests



def send_message(message):
    token = os.environ.get('slack_token')


    url = "https://slack.com/api/chat.postMessage"

    querystring = {"token":token,"channel":"@praveenkumar.s","text":message,"username":"Aha_Syncer","parse":"full","link_names":"1"}


    response = requests.request("GET", url, params=querystring)

    print(response.text)

def features_format_message(feature_update):
    finalstr=''
    for items in feature_update:
        k=list(items.keys())[0]
        if(len(items[k])!=0):
            finalstr=finalstr+' '+k+' -->  '+str(items[k])+'\n'

    return(finalstr)
