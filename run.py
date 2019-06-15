import os
import sys
import signal
import json
import requests
from time import sleep
import datetime
from pydnserver import DNSServer

########## pydnserver ##########
# Set the config initialisation parameters
# Constants for accessing config items
REDIRECT_HOST = u'redirect_host'
ACTIVE = u'active'
########## pydnserver ##########

def updateHosts(dns, hostnames):
    lookup_map = {}
    for item in hostnames:
        lookup_map[item['hostname'] + '.' + item['namespace'] + '.podname.cluster.local'] = {'redirect_host': item['podIP'], 'active': True}
    dns.set_host_list(lookup_map)

token_path = os.environ['SERVICEACCOUNT_PATH'] + '/token'
URL = os.environ['KUBEAPI_URL'] + '/api/v1/pods'

def handler(signum, frame):
    print('Signal handler called with signal', signum)
    exit(0)


signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

dns = DNSServer(interface = "0.0.0.0", port = 53)
dns.start()

sleep(1)

prev_hostnames = []

err_count = -1
while True:
    if err_count != 0:
        f = open(token_path, 'r')
        token = ''.join(f.readlines()).strip()
        f.close()
        
    response = requests.get(URL, headers={'Authorization': 'Bearer ' + token})
    
    if response.status_code == 200:
        err_count = 0
        res = json.loads(response.text)

        hostnames = []

        for item in res['items']:
            try:
                hostnames.append({'namespace': item['metadata']['namespace'], 'hostname': item['metadata']['name'], 'podIP': item['status']['podIP']})
            except:
                print("Unexpected error:", sys.exc_info()[0], " META:", item['metadata'], " STAT:", item['status'])

        if prev_hostnames != hostnames:
            print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ": CHANGED!")
            updateHosts(dns, hostnames)
            
        prev_hostnames = hostnames
        
        sleep(3)
    else:
        print("Error: ", response.status_code, response.text)
        err_count += 1
        if err_count >= 10:
            exit(response.status_code)
        
        sleep(2)



