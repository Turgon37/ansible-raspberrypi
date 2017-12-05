#!/usr/bin/env python

import json
import os
import re
import subprocess
import sys

content=dict({
  'codecs_enabled': [],
  'codecs_disabled': [],
})

device_tree_dir = '/proc/device-tree'
model_file = device_tree_dir  + '/model'

codecs_names = ['H264', 'MPG2', 'WVC1', 'MPG4', 'MJPG', 'WMV9']

firmware_version_re = re.compile('^version\s+(?P<version>[^ ]+)')
hardware_version_re = re.compile('^Hardware[:\s]+(?P<version>[^ ]+)')
revision_version_re = re.compile('^Revision[:\s]+(?P<version>[^ ]+)')
serial_version_re = re.compile('^Serial[:\s]+(?P<version>[^ ]+)')

stripped = lambda s: "".join(i for i in s if 31 < ord(i) < 127)

# use https://github.com/AndrewFromMelbourne/raspberry_pi_revision/blob/master/raspberry_pi_revision.c
revision_mapping = dict({
  '0002': {'model': 'B Rev 1', 'ram': '256MB'},
  '0003': {'model': 'ECN0001 (no fuses, D14 removed)', 'ram': '256MB'},
  '0004': {'model': 'B Rev 2', 'ram': '256MB', 'manufacturer': 'Sony', 'comment': '(Mfg by Sony)'},
  '0004': {'model': 'B', 'ram': '256 MB'},
  '0005': {'model': 'B', 'ram': '256 MB', 'comment': '(Mfg by Qisda)'},
  '0006': {'model': 'B', 'ram': '256 MB', 'comment': '(Mfg by Egoman)'},
  '0007': {'model': 'A', 'ram': '256 MB', 'comment': '(Mfg by Egoman)'},
  '0008': {'model': 'A', 'ram': '256 MB', 'comment': '(Mfg by Sony)'},
  '0009': {'model': 'A', 'ram': '256 MB', 'comment': '(Mfg by Qisda)'},
  '000d': {'model': 'B', 'ram': '512 MB', 'comment': '(Mfg by Egoman)'},
  '000e': {'model': 'B', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  '000f': {'model': 'B', 'ram': '512 MB', 'comment': '(Mfg by Qisda)'},
  '0010': {'model': 'B+', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  '0011': {'model': 'Compute Module 1', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  '0012': {'model': 'A+', 'ram': '256 MB', 'comment': '(Mfg by Sony)'},
  '0013': {'model': 'B+', 'ram': '512 MB'},
  '0014': {'model': 'Compute Module 1', 'ram': '512 MB', 'country': 'China', 'comment': '(Mfg by Embest)'},
  '0015': {'model': 'A+', 'ram': '256 MB / 512 MB', 'country': 'China', 'comment': '(Mfg by Embest)'},
  'a01040': {'model': '2 Model B', 'model_version_major': 2, 'ram': '1 GB', 'comment': '(Mfg by Sony)'},
  'a01041': {'model': '2 Model B', 'model_version_major': 2, 'ram': '1 GB', 'country': 'UK', 'comment': '(Mfg by Sony)'},
  'a21041': {'model': '2 Model B', 'model_version_major': 2, 'ram': '1 GB', 'country': 'China', 'comment': '(Mfg by Embest)'},
  'a22042': {'model': '2 Model B (with BCM2837)', 'model_version_major': 2, 'ram': '1 GB', 'comment': '(Mfg by Embest)'},
  '900021': {'model': 'A+', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  '900032': {'model': 'B+', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  '900092': {'model': 'Zero', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  '900093': {'model': 'Zero', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  '920093': {'model': 'Zero', 'ram': '512 MB', 'comment': '(Mfg by Embest)'},
  '9000c1': {'model': 'Zero W', 'ram': '512 MB', 'comment': '(Mfg by Sony)'},
  'a02082': {'model': '3 Model B', 'model_version_major': 3, 'ram': '1 GB', 'comment': '(Mfg by Sony)'},
  'a020a0': {'model': 'Compute Module 3 (and CM3 Lite)', 'ram': '1 GB', 'country': 'UK', 'comment': '(Mfg by Sony)'},
  'a22082': {'model': '3 Model B', 'model_version_major': 3, 'ram': '1 GB', 'country': 'China', 'comment': '(Mfg by Embest)'},
  'a32082': {'model': '3 Model B', 'model_version_major': 3, 'ram': '1 GB', 'comment': '(Mfg by Sony Japan)'},
})

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
        # HARDWARE
        match = hardware_version_re.search(line)
        if match:
            content['hardware'] = match.group('version')
        # REVISION
        match = revision_version_re.search(line)
        if match:
            content['hardware_revision'] = match.group('version')
            if content['hardware_revision'] in revision_mapping:
                content['hardware_revision_informations'] = revision_mapping[content['hardware_revision']]
                revision_hex = int(content['hardware_revision'], 16)
        # SERIAL VERSION
        match = serial_version_re.search(line)
        if match:
            content['hardware_serial'] = match.group('version')
    # Device informations
    if os.path.isfile(model_file):
        hdl = open(model_file, 'r')
        content['model_string'] = stripped(hdl.read())
    # Codecs informations
    for codec in codecs_names:
        result = subprocess.check_output(['/usr/bin/env', 'vcgencmd', 'codec_enabled', codec], universal_newlines=True)
        if 'enabled' in result:
            content['codecs_enabled'].append(codec)
        else:
            content['codecs_disabled'].append(codec)
except subprocess.CalledProcessError as e:
    content['error'] = str(e)

if len(content) == 0:
    content = None

print(json.dumps(content))
sys.exit(0)
