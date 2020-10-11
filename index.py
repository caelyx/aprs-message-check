#!/usr/bin/python3

import requests
import json
import datetime
import dbm
import os

from config import APIKEY,CALLSIGNS,EMAIL

DATABASE = 'seen_msgs'

def main():
    """Email a summary of new APRS messages.

    Steps:
    * Poll APRS.FI for messages involving given callsigns, 
    * filter out ones previously reported, and 
    * email any new messages to EMAIL.

    Stores previously seen message IDs in a DBM database in the local 
    filesystem. If it gets too large or if errors occur, just delete 
    it, as the worst-case impact is it emails you again for messages 
    you've already seen.
    """

    requestString = 'https://api.aprs.fi/api/get?what=msg&dst=%s&apikey=%s&format=json' % (CALLSIGNS, APIKEY)

    r = requests.get(requestString)
    #print("Request status code: ", r.status_code)
    assert r.status_code == 200 # TODO Lazy
    data = r.json()

    db = dbm.open(DATABASE, 'c')

    newmessages = False 
    fp_messages = open('messages.txt', 'w')

    for e in data['entries']:
        timestamp = datetime.datetime.fromtimestamp(int(e['time']))
        e['timestamp'] = timestamp.strftime("%F %H:%M")
        #Key fields: e['messageid'] e['srccall'], e['dst'], e['message']
        if not e['messageid'] in db:
            newmessages = True
            # print ('New message:', e['messageid'])
            fp_messages.write("%s -> %s -> %s (%s UTC)" %(e['srccall'], e['dst'], e['message'], e['timestamp']))
            fp_messages.write("\n\n")
            fp_messages.write(str(e))
            fp_messages.write("\n\n\n")
            # print(e)
            db[ e['messageid'] ] = e['timestamp']

    fp_messages.close()

    if newmessages:
        os.system('mail -s "New APRS Messages" %s < messages.txt' % EMAIL)
    #else:
    #   print ("No new messages.")
    
    db.close()



if __name__ == "__main__":
    main()
