#
# Copyright 2010 Red Hat, Inc. and/or its affiliates.
#
# Licensed to you under the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  See the files README and
# LICENSE_GPL_v2 which accompany this distribution.
#

import os, platform, time

try:
    import json
except ImportError:
    import simplejson as json

class VirtIoChannel:

    # Python on Windows 7 return 'Microsoft' rather than 'Windows' as documented.
    is_windows = (platform.system() == 'Windows') or (platform.system() == 'Microsoft')

    def __init__(self, vport_name):
        if self.is_windows:
            from WinFile import WinFile
            self._vport = WinFile(vport_name)
        else:
            self._vport = os.open(vport_name, os.O_RDWR)
        self._buffer = ''

    def _readbuffer(self):
        if self.is_windows:
            buffer = self._vport.read(4096)
        else:
            buffer = os.read(self._vport, 4096)
        if buffer:
            self._buffer += buffer
        else:
            # read() returns immediately (non-blocking) if no one is
            # listening on the other side of the virtio-serial port.
            # So in order not to be in a tight-loop and waste CPU
            # time, we just sleep for a while and hope someone will
            # be there when we will awake from our nap.
            time.sleep(1)

    def _readline(self):
        newline = self._buffer.find('\n')
        while newline < 0:
            self._readbuffer()
            newline = self._buffer.find('\n')
        if newline >= 0:
            line, self._buffer = self._buffer.split('\n', 1)
        else:
            line = None
        return line

    def _parseLine(self, line):
        try:
            args = json.loads(line.decode('utf8'))
            name = args['__name__']
            del args['__name__']
        except:
            name = None
            args = None
        return (name, args)

    def read(self):
        return self._parseLine(self._readline())

    def write(self, name, args = {}):
        if not isinstance(name, str):
            raise TypeError("1nd arg must be a str.")
        if not isinstance(args, dict):
            raise TypeError("2nd arg must be a dict.")
        args['__name__'] = name
        message = (json.dumps(args) + '\n').encode('utf8')
        while len(message) > 0:
            if self.is_windows:
                written = self._vport.write(message)
            else:
                written = os.write(self._vport, message)
            message = message[written:]

def _create_vio():
    if (platform.system() == 'Windows') or (platform.system() == 'Microsoft'):
        vport_name = '\\\\.\\Global\\com.redhat.rhevm.vdsm'
    else:
        vport_name = '/dev/virtio-ports/com.redhat.rhevm.vdsm'
    return VirtIoChannel(vport_name)

def _test_write():
    vio = _create_vio()
    vio.write('network-interfaces', { 'interfaces' :
        [{ 'name': 'eth0', 'inet': [ '10.0.0.2' ], 'inet6': [ 'fe80::213:20ff:fef5:f9d6' ], 'hw': '00:1a:4a:23:10:00' }] })
    vio.write('applications', { 'applications' : [ 'kernel-2.6.32-131.4.1.el6', 'rhev-agent-2.3.11-1.el6'] })

def _test_read():
    vio = _create_vio()
    line = vio.read()
    while line:
        print line
        line = vio.read()

if __name__ == "__main__":
    _test_read()
