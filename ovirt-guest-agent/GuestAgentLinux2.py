#!/usr/bin/python
#
# Copyright 2010-2012 Red Hat, Inc. and/or its affiliates.
#
# Licensed to you under the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  See the files README and
# LICENSE_GPL_v2 which accompany this distribution.
#

import os, rpm, socket, subprocess, string, threading, logging
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
        self.app_list = ""
        self.ignored_fs = ""

    def getMachineName(self):
        return socket.getfqdn()

    def getOsVersion(self):
        return os.uname()[2]

    def getAllNetworkInterfaces(self):
        interfaces = list()
        try:
            for dev in ethtool.get_active_devices():
                flags = ethtool.get_flags(dev)
                if not(flags & ethtool.IFF_LOOPBACK):
                    devinfo = ethtool.get_interfaces_info(dev)[0]
                    interfaces.append({ 'name' : dev,
                        'inet' : [ ethtool.get_ipaddr(dev) ],
                        'inet6' : map(lambda ip: ip.address, devinfo.get_ipv6_addresses()),
                        'hw' : ethtool.get_hwaddr(dev) })
        except:
            logging.exception("Error retrieving network interfaces.")
        return interfaces

    def getApplications(self):
        apps = []
        try:
            for name in self.app_list.split():
                ts = rpm.TransactionSet()
                mi = ts.dbMatch('name', name)
                try:
                    while mi:
                        app = mi.next()
                        apps.append("%s-%s-%s" % (app['name'], app['version'], app['release']))
                except StopIteration:
                    pass
        except:
            logging.exception("Error retrieving installed applications.")
        return apps

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

if __name__ == '__main__':
    test()
