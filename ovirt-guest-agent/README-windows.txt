oVirt Guest Agent for Windows - Howto setup devel environment
===========================================================
Supported guest OSs:
- xp
- windows 7 (32/64)
- windows 2003 (32/64/r2)
- windows 2008 (32/64/r2)

Please note that we always use the 32 bit python even on 64 bit platforms


Requirements:
-------------

Install Python 2.6.6 for Windows.
(http://www.python.org/ftp/python/2.6.6/python-2.6.6.msi)

Install Python for Windows extension (pywin32) version 216 for Python 2.6
(http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.6.exe/download)

Optionally install py2exe if you want to build an executable file which
doesn't require Python installation for running
(http://sourceforge.net/projects/py2exe/files/py2exe/0.6.9/py2exe-0.6.9.win32-py2.6.exe/download)

Source code modifications:
--------------------------

Update the AGENT_CONFIG global variable in OVirtGuestService.py to point to
right configuration location.

Running the service:
--------------------

> python OVirtGuestService.py -install
> net OVirtGuestService start

Building executable file:
-------------------------

> python setup.py py2exe -b 1
