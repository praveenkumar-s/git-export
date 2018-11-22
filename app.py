import aha_zen_adapter
import aha_zen_master_feature_importer
import slack_sender
import requests
from datetime import datetime

def upload_to_storage(data):
    rs=requests.post('https://funteam.herokuapp.com/insertresults', data= str(data))
    if(rs.status_code==200):
        return 'https://funteam.herokuapp.com/getautomationresults?key='+rs.content
    else:
        return ''


feature_update=aha_zen_adapter.main()

slack_sender.send_message('Features Sync happened @ '+str(datetime.now)+ ' logs @ ' +upload_to_storage(feature_update))
master_feature_update=aha_zen_master_feature_importer.main()
slack_sender.send_message('Master Features Sync happened @ '+str(datetime.now)+ ' logs @ ' +upload_to_storage(master_feature_update))

