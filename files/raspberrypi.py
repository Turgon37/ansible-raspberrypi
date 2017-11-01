#!/usr/bin/env python

import json
import os
import re
import subprocess
import sys

content=dict()


firmware_version_re = re.compile('^version\s+(?P<version>[^ ]+)')
hardware_version_re = re.compile('^Hardware[:\s]+(?P<version>[^ ]+)')
revision_version_re = re.compile('^Revision[:\s]+(?P<version>[^ ]+)')
serial_version_re = re.compile('^Serial[:\s]+(?P<version>[^ ]+)')

try:
    # Firmware version
    result = subprocess.check_output(['/usr/bin/env', 'vcgencmd', 'version'], universal_newlines=True)
    for line in result.split('\n'):
        match = firmware_version_re.search(line)
        if match:
            content['firmware_version'] = match.group('version')
    # CPU informations
    hdl = open('/proc/cpuinfo', 'r')
    for line in hdl.readlines():
        line = line.strip()
        match = hardware_version_re.search(line)
        if match:
            content['hardware'] = match.group('version')
        match = revision_version_re.search(line)
        if match:
            content['hardware_revision'] = match.group('version')
        match = serial_version_re.search(line)
        if match:
            content['hardware_serial'] = match.group('version')
except subprocess.CalledProcessError as e:
    content['error'] = str(e)

if len(content) == 0:
    content = None

print(json.dumps(content))
sys.exit(0)