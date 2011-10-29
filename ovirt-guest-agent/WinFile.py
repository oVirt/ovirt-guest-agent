#!/usr/bin/python
#
# Copyright 2011 Red Hat, Inc. and/or its affiliates.
#
# Licensed to you under the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  See the files README and
# LICENSE_GPL_v2 which accompany this distribution.
#

import win32security
import win32file
import win32event
import win32con
import pywintypes

# Using Python's os.read() to do a blocking-read doesn't allow
# to use os.write() on a different thread. This class overrides
# this problem by using Windows's API.

class WinFile(object):

    def __init__(self, filename):
        self._hfile = win32file.CreateFile(filename,
            win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            win32security.SECURITY_ATTRIBUTES(),
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_OVERLAPPED,
            0)
        self._read_ovrlpd = pywintypes.OVERLAPPED()
        self._read_ovrlpd.hEvent = win32event.CreateEvent(None, True, False, None)
        self._write_ovrlpd = pywintypes.OVERLAPPED()
        self._write_ovrlpd.hEvent = win32event.CreateEvent(None, True, False, None)

    def read(self, n):
        (nr, buf) = (0, ())
        try:
            (hr, buf) = win32file.ReadFile(self._hfile, win32file.AllocateReadBuffer(n), self._read_ovrlpd)
            nr = win32file.GetOverlappedResult(self._hfile, self._read_ovrlpd, True)
        except:
            pass
        return buf[:nr]

    def write(self, s):
        win32file.WriteFile(self._hfile, s, self._write_ovrlpd)
        return win32file.GetOverlappedResult(self._hfile, self._write_ovrlpd, True)
