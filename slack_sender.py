import os
import requests



def send_message(message):
    token = os.environ.get('slack_token')


    url = "https://slack.com/api/chat.postMessage"

    querystring = {"token":token,"channel":"@praveenkumar.s","text":message,"username":"Aha_Syncer","parse":"full","link_names":"1"}


    response = requests.request("GET", url, params=querystring)

    print(response.text)