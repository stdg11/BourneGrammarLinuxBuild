#! /usr/bin/python
# Daniel Grammatica | dan@t0xic.me
# https://github.com/stdg11/BourneGrammarLinuxBuild
#
# Script to process xml results from Export-DhcpServer Powershell command
# Into JSON and create Cobbler systems
#
# Powershell command:
# Export-DhcpServer -ScopeId 10.0.72.0 -File dhcp-export.xml -Leases -Force
#
# Usage:
# ./dhcp-import.py filename.xml
#
# TODO: Add skip systems sysarg --skip


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
        hostname = "L" + record[0]
        raw_mac = record [1]
        mac = raw_mac.replace('-',':')
        try:
            print(hostname)
            count += 1
        except:
            print ("%s NOT Added" % hostname)
            pass
except:
    pass

print (" %s Systems processed" % (count)) 
