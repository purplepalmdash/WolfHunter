#!/usr/bin/env python

import sys
import json
import ansible.runner
import time

# specify hosts from inventory we should contact
#hostlist = [ 'localhost', '127.0.0.1' ]
#hostlist = [ 'dashArch']
hostlist = [ 'localhost']
#hostlist = [ 'dashArch','10.3.3.1' ]

def gigs(kibs):
    return float(kibs) / 1024.0 / 1024.0

runner = ansible.runner.Runner(
    module_name='my-df',
    module_args='',
    remote_user='dash',
    #sudo=False,
    pattern=':'.join(hostlist),
)

# Ansible now pops off to do it's thing via SSH
response = runner.run()
#time.sleep(5)
print type(response)
print response

# We're back.
# Check for failed hosts

if 'dark' in response:
    if len(response['dark']) > 0:
        print "Contact failures:"
        for host, reason in response['dark'].iteritems():
            print "  %s (%s)" % (host, reason['msg'])


total = 0.0
for host, res in response['contacted'].iteritems():
    print host
    print "#################################"
    for fs in res['space']:
        gb = gigs(fs['available'])
        total += gb
        print "  %-30s %10.2f" % (fs['mountpoint'], gb)

print "Total space over %d hosts: %.2f GB" % (len(response['contacted']), total)
