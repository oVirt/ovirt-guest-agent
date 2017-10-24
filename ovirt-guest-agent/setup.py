
from distutils.core import setup
from glob import glob
import os
import sys

import py2exe

if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-b 1")


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = "1.0.14"
        self.company_name = "Red Hat"
        self.copyright = "Copyright(C) Red Hat Inc."
        self.name = "Guest VDS Agent "

OVirtAgentTarget = Target(description="Ovirt Guest Agent",
                          modules=["OVirtGuestService"])

DLL_EXCLUDES = ['POWRPROF.dll', 'KERNELBASE.dll',
                'WTSAPI32.dll', 'MSWSOCK.dll']
for name in glob(os.getenv('windir') + '\*\API-MS-Win-*.dll'):
    DLL_EXCLUDES.append(name[name.rfind('\\') + 1:])

setup(service=[OVirtAgentTarget],
      options={'py2exe': {
          'bundle_files': 1,
          'dll_excludes': DLL_EXCLUDES}},
      zipfile=None)
