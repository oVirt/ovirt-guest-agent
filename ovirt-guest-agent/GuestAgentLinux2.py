#
# Copyright 2010-2012 Red Hat, Inc. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Refer to the README and COPYING files for full details of the license.
#

import os, socket, subprocess, string, threading, logging, time
import ethtool
from OVirtAgentLogic import AgentLogicBase, DataRetriverBase

try:
    from CredServer import CredServer
except ImportError:
    # The CredServer doesn't exist in RHEL-5. So we provide a
    # fake server that do nothing.
    class CredServer(threading.Thread):
        def user_authenticated(self, credentials):
            pass

class PkgMgr(object):

    def rpm_list_packages(self, app_list):
        apps = []
        for name in app_list.split():
            ts = self.rpm.TransactionSet()
            for app in ts.dbMatch('name', name):
                apps.append("%s-%s-%s" %
                    (app['name'], app['version'], app['release']))
        return apps

    def __init__(self):
        if os.path.exists('/etc/redhat-release'):
            import rpm
            self.rpm = rpm
            self.list_pkgs = self.rpm_list_packages
        else:
            raise NotImplementedError

class NicMgr(object):

    def ethtool_list_nics(self):
        interfaces = list()
        try:
            for dev in self.ethtool.get_active_devices():
                flags = self.ethtool.get_flags(dev)
                if not(flags & self.ethtool.IFF_LOOPBACK):
                    devinfo = self.ethtool.get_interfaces_info(dev)[0]
                    interfaces.append({ 'name' : dev,
                        'inet' : [ self.ethtool.get_ipaddr(dev) ],
                        'inet6' : map(lambda ip: ip.address,
                            devinfo.get_ipv6_addresses()),
                        'hw' : self.ethtool.get_hwaddr(dev) })
        except:
            logging.exception("Error retrieving network interfaces.")
        return interfaces

    def __init__(self):
        try:
            import ethtool
        except ImportError:
            raise NotImplementedError
        self.ethtool = ethtool
        self.list_nics = self.ethtool_list_nics

class CommandHandlerLinux:

    def __init__(self, agent):
        self.agent = agent

    def lock_screen(self):
        cmd = [ '/usr/share/ovirt-guest-agent/ovirt-locksession' ]
        logging.debug("Executing lock session command: '%s'", cmd)
        subprocess.call(cmd)

    def login(self, credentials):
        self.agent.cred_server.user_authenticated(credentials)

    def logoff(self):
        pass

    def shutdown(self, timeout, msg):
        # The shutdown command works with minutes while vdsm send value in
        # seconds, so we round up the value to minutes.
        delay = (int(timeout) + 59) / 60
        cmd = [ '/usr/share/ovirt-guest-agent/ovirt-shutdown', '-h', "+%d" % (delay), "\"%s\"" % (msg) ]
        logging.debug("Executing shutdown command: %s", cmd)
        subprocess.call(cmd)

    def hibernate(self, state):
        cmd = [ '/usr/share/ovirt-guest-agent/ovirt-hibernate', state ]
        logging.debug("Executing hibernate command: %s", cmd)
        subprocess.call(cmd)

class LinuxDataRetriver(DataRetriverBase):

    def __init__(self):
        try:
             pkgmgr = PkgMgr()
        except NotImplementedError:
             self.list_pkgs = lambda app_list: []
        else:
             self.list_pkgs = pkgmgr.list_pkgs
        try:
             nicmgr = NicMgr()
        except NotImplementedError:
             self.list_nics = lambda: []
        else:
             self.list_nics = nicmgr.list_nics
        self.app_list = ""
        self.ignored_fs = ""
        self._init_vmstat()
        DataRetriverBase.__init__(self)

    def getMachineName(self):
        return socket.getfqdn()

    def getOsVersion(self):
        return os.uname()[2]

    def getAllNetworkInterfaces(self):
        return self.list_nics()

    def getApplications(self):
        return self.list_pkgs(self.app_list)

    def getAvailableRAM(self):
        free = 0
        for line in open('/proc/meminfo'):
            var, value = line.strip().split()[0:2]
            if var in ('MemFree:', 'Buffers:', 'Cached:'):
                free += long(value)
        return str(free / 1024)

    def getUsers(self):
        users = ''
        try:
            cmdline = '/usr/bin/users | /usr/bin/tr " " "\n" | /usr/bin/uniq'
            users = string.join(string.join(os.popen(cmdline).readlines()).split())
        except:
            logging.exception("Error retrieving logged in users.")
        return users

    def getActiveUser(self):
        users = string.join(os.popen('/usr/bin/users').readlines()).split()
        try:
            user = users[0]
        except:
            user = 'None'
        return user

    def getDisksUsage(self):
        usages = list()
        try:
            mounts = open('/proc/mounts')
            for mount in mounts:
                (device, path, fs) = mount.split()[:3]
                if not fs in self.ignored_fs:
                    # path might include spaces.
                    path = path.decode("string-escape")
                    statvfs = os.statvfs(path)
                    total = statvfs.f_bsize * statvfs.f_blocks
                    used = total - statvfs.f_bsize * statvfs.f_bfree
                    usages.append({ 'path' : path, 'fs' : fs, 'total' : total, 'used' : used })
            mounts.close()
        except:
            logging.exception("Error retrieving disks usages.")
        return usages

    def getMemoryStats(self):
        try:
            self._get_meminfo()
            self._get_vmstat()
        except:
            logging.exception("Error retrieving memory stats.")
        return self.memStats

    def _init_vmstat(self):
        self.vmstat = {}
        self.vmstat['timestamp_prev'] = time.time()
        fields = ['swap_in', 'swap_out', 'pageflt', 'majflt']
        for field in fields:
            self.vmstat[field + '_prev'] = None
            self.vmstat[field + '_cur'] = None

    def _get_meminfo(self):
        fields = {'MemTotal:' : 0, 'MemFree:' : 0, 'Buffers:' : 0, \
                  'Cached:' : 0}
        free = 0
        for line in open('/proc/meminfo'):
            (key, value) = line.strip().split()[0:2]
            if key in fields.keys():
                fields[key] = int(value)
            if key in ('MemFree:', 'Buffers:', 'Cached:'):
                free += int(value)
        self.memStats['mem_total'] = fields['MemTotal:']
        self.memStats['mem_unused'] = fields['MemFree:']
        self.memStats['mem_free'] = free

    def _get_vmstat(self):
        """
        /proc/vmstat reports cumulative statistics so we must subtract the
        previous values to get the difference since the last collection.
        """
        fields = {'pswpin' : 'swap_in', 'pswpout' : 'swap_out',
                        'pgfault' : 'pageflt', 'pgmajfault' : 'majflt'}

        self.vmstat['timestamp_cur'] = time.time()
        interval = self.vmstat['timestamp_cur'] - self.vmstat['timestamp_prev']
        self.vmstat['timestamp_prev'] = self.vmstat['timestamp_cur']

        for line in open('/proc/vmstat'):
            (key, value) = line.strip().split()[0:2]
            if key in fields.keys():
                name = fields[key]
                self.vmstat[name + '_prev'] = self.vmstat[name + '_cur']
                self.vmstat[name + '_cur'] = int(value)
                if self.vmstat[name + '_prev'] == None:
                    self.vmstat[name + '_prev'] = self.vmstat[name + '_cur']
                self.memStats[name] = int((self.vmstat[name + '_cur'] - \
                                self.vmstat[name + '_prev'])/interval)


class LinuxVdsAgent(AgentLogicBase):

    def __init__(self, config):
        AgentLogicBase.__init__(self, config)
        self.dr = LinuxDataRetriver()
        self.dr.app_list = config.get("general", "applications_list")
        self.dr.ignored_fs = set(config.get("general", "ignored_fs").split())
        self.commandHandler = CommandHandlerLinux(self)
        self.cred_server = CredServer()

    def run(self):
        self.cred_server.start()
        AgentLogicBase.run(self)

    def stop(self):
        self.cred_server.join()
        AgentLogicBase.stop(self)

def test():
    dr = LinuxDataRetriver()
    dr.app_list = "kernel kernel-headers aspell"
    dr.ignored_fs = set("rootfs tmpfs autofs cgroup selinuxfs udev mqueue nfsd " \
        "proc sysfs devtmpfs hugetlbfs rpc_pipefs devpts securityfs debugfs " \
        "binfmt_misc".split())
    print "Machine Name:", dr.getMachineName()
    print "OS Version:", dr.getOsVersion()
    print "Network Interfaces:", dr.getAllNetworkInterfaces()
    print "Installed Applications:", dr.getApplications()
    print "Available RAM:", dr.getAvailableRAM()
    print "Logged in Users:", dr.getUsers()
    print "Active User:", dr.getActiveUser()
    print "Disks Usage:", dr.getDisksUsage()
    print "Memory Stats:", dr.getMemoryStats()

if __name__ == '__main__':
    test()
