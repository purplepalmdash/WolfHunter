#!/usr/bin/env python

import subprocess
import json

space = []

df = subprocess.Popen(["df", "-P", "-k"], stdout=subprocess.PIPE)
output = df.communicate()[0]

print "See this means we really calls this subprocess!"

for line in output.split("\n")[1:]:
    print line
    if len(line):
        try:
            device, size, used, available, percent, mountpoint = line.split()
            space.append(dict(mountpoint=mountpoint, available=available))
        except:
            pass

print json.dumps(dict(space=space), indent=4)
