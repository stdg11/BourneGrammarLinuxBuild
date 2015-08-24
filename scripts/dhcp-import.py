#! /usr/bin/python
# Daniel Grammatica | dan@t0xic.me
# https://github.com/stdg11/BourneGrammarLinuxBuild
# Script to process xml results from Export-DhcpServer Powershell command
# Into JSON and create Cobbler systems

import sys,xmltodict,subprocess

filename = sys.argv[1] # Retrieve the file name given after dhcp-import.py
file = open(filename, "r") # Open filename Read only
xml = file.read() # Read the contents of the file into variable xml
json = xmltodict.parse(xml) # Parse xml into JSON style dictionary
leases = json['DHCPServer']['IPv4']['Scopes']['Scope']['Leases']['Lease'] # Retrieve each lease
count = 0 

try:
    for lease in leases:
        record = (lease['HostName'], lease['ClientId'])
        hostname = record[0]
        raw_mac = record [1]
        mac = raw_mac.replace('-',':')
        subprocess.call(['cobbler', 'system', 'add', '--name=%s' % hostname , '--profile=ubuntu-server-x86_64', '--mac=%s' % mac, '--interface=eth0'])
        print ("%s Added Succesfully" % hostname)
        count += 1
except:
    pass

print (" %s Systems processed" % (count)) 
