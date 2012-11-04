#!/usr/bin/python

import time, os, logging, types
import win32netcon
import win32net
import win32ts
import win32api
import win32pipe
import win32security
import win32process
import win32con
import win32com.client
import pythoncom
import subprocess
import socket
from OVirtAgentLogic import AgentLogicBase, DataRetriverBase
from ctypes import *
from ctypes.util import find_library
from ctypes.wintypes import *
import _winreg

# Both _winreg.QueryValueEx and win32api.RegQueryValueEx doesn't support reading
# Unicode strings from the registry (at least on Python 2.5.1).
def QueryStringValue(hkey, name):
    #if type(hkey) != type(PyHKEY):
    #    raise TypeError("1nd arg must be a PyHKEY.")
    if type(name) != type(unicode()):
        raise TypeError("2nd arg must be a unicode.")
    key_type = c_ulong(0)
    key_len = c_ulong(0)
    if windll.advapi32.RegQueryValueExW(hkey.handle, name, None, byref(key_type), None, byref(key_len)) != 0:
        return unicode()
    if (key_type.value != win32con.REG_SZ):
        return unicode()
    key_value = create_unicode_buffer(key_len.value)
    if windll.advapi32.RegQueryValueExW(hkey.handle, name, None, None, byref(key_value), byref(key_len)) != 0:
        return unicode()
    return key_value.value

def GetNetworkInterfaces():
    interfaces = list()
    try:
        objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
        objSWbemServices = objWMIService.ConnectServer(".", "root\cimv2")
        adapters = objSWbemServices.ExecQuery(
            "SELECT * FROM Win32_NetworkAdapterConfiguration")
        for adapter in adapters:
            if adapter.IPEnabled:
                inet = []
                inet6 = []
                if adapter.IPAddress:
                    for ip in adapter.IPAddress:
                        try:
                            socket.inet_aton(ip)
                            inet.append(ip)
                        except socket.error:
                            # Assume IPv6 if parsing as IPv4 was failed.
                            inet6.append(ip)
                interfaces.append({ 'name' : adapter.Description,
                    'inet' : inet, 'inet6' : inet6,
                    'hw' : adapter.MacAddress.lower() })
    except:
        logging.exception("Error retrieving network interfaces.")
    return interfaces

class PERFORMANCE_INFORMATION(Structure):
    _fields_ = [
        ('cb', DWORD),
        ('CommitTotal', DWORD),
        ('CommitLimit', DWORD),
        ('CommitPeak', DWORD),
        ('PhysicalTotal', DWORD),
        ('PhysicalAvailable', DWORD),
        ('SystemCache', DWORD),
        ('KernelTotal', DWORD),
        ('KernelPaged', DWORD),
        ('KernelNonpaged', DWORD),
        ('PageSize', DWORD),
        ('HandleCount', DWORD),
        ('ProcessCount', DWORD),
        ('ThreadCount', DWORD)
    ]

def get_perf_info():
    pi = PERFORMANCE_INFORMATION()
    pi.cb = sizeof(pi)
    windll.psapi.GetPerformanceInfo(byref(pi), pi.cb)
    return pi

class IncomingMessageTypes:
        Credentials = 11

class WinOsTypeHandler:
    WINNT3_51  = 'Win NT 3.51'
    WINNT4     = 'Win NT 4'
    WIN2K      = 'Win 2000'
    WINXP      = 'Win XP'
    WIN2003    = 'Win 2003'
    WIN2008    = 'Win 2008'
    WIN2008R2  = 'Win 2008 R2'
    WIN2012    = 'Win 2012'
    WIN7       = 'Win 7'
    WIN8       = 'Win 8'
    WINCE3_1_0 = 'Win CE 1.0'
    WINCE3_2_0 = 'Win CE 2.0'
    WINCE3_2_1 = 'Win CE 2.1'
    WINCE3_3_0 = 'Win CE 3.0'
    UNKNOWN    = 'Unknown'
    #winVersionMatrix is constructed from 3 fields <platformId>.<MajorVersion>.<MinorVersion>
    winVersionMatrix = {
        '2.3.51' : WINNT3_51,
        '2.4.0'  : WINNT4,
        '2.5.0'  : WIN2K,
        '2.5.1'  : WINXP,
        '2.5.2'  : WIN2003,
        '2.6.0'  : WIN2008,
        '2.6.1'  : WIN2008R2, # Window Server 2008 R2
        '2.6.2'  : WIN2012,
        '3.1.0'  : WINCE3_1_0,
        '3.2.0'  : WINCE3_2_0,
        '3.2.1'  : WINCE3_2_1 ,
        '3.3.0'  : WINCE3_3_0}
    def getWinOsType(self):
        retval = self.UNKNOWN
        try:
            versionTupple = win32api.GetVersionEx(1)
            key = "%d.%d.%d" % (
                versionTupple[3], versionTupple[0], versionTupple[1])
            if self.winVersionMatrix.has_key(key):
                retval = self.winVersionMatrix[key]
            # Window 7 and Window Server 2008 R2 share the same version.
            # Need to fix it using the wProductType field.
                VER_NT_WORKSTATION = 1
            if (retval == WinOsTypeHandler.WIN2008R2 and
                versionTupple[8] == VER_NT_WORKSTATION):
                    retval = WinOsTypeHandler.WIN7
            elif (retval == WinOsTypeHandler.WIN2012 and
                  versionTupple[8] == VER_NT_WORKSTATION):
                retval = WinOsTypeHandler.WIN8
            logging.debug("WinOsTypeHandler::getWinOsType osType = '%s'", retval)
        except:
            logging.exception("getWinOsType - failed")
        return retval

class CommandHandlerWin:

    def lock_screen(self):
        self.LockWorkStation()

    def login(self, credentials):
        PIPE_NAME = "\\\\.\\pipe\\VDSMDPipe"
        BUFSIZE = 1024
        RETIRES = 3
        try:
            if find_library('sas') is not None:
                logging.debug("Simulating a secure attention sequence (SAS).")
                windll.sas.SendSAS(0)
            retries = 1
            while retries <= RETIRES:
                try:
                    time.sleep(1)
                    win32pipe.CallNamedPipe(PIPE_NAME, credentials, BUFSIZE, win32pipe.NMPWAIT_WAIT_FOREVER)
                    logging.debug("Credentials were written to pipe.")
                    break
                except:
                    error = windll.kernel32.GetLastError()
                    logging.error("Error writing credentials to pipe [%d/%d] (error = %d)", retries, RETIRES, error)
                    retries += 1
        except:
            logging.exception("Error occurred during user login.")

    def logoff(self):
        sessionId = win32ts.WTSGetActiveConsoleSessionId()
        if sessionId != 0xffffffff:
            logging.debug("Logging off current user (session %d)", sessionId)
            win32ts.WTSLogoffSession(win32ts.WTS_CURRENT_SERVER_HANDLE, sessionId, 0)
        else:
            logging.debug("No active session. Ignoring log off command.")

    def shutdown(self, timeout, msg):
        cmd = "%s\\system32\\shutdown.exe -s -t %d -f -c \"%s\"" % (os.environ['WINDIR'], timeout, msg)
        logging.debug("Executing shutdown command: '%s'", cmd)

        # Since we're a 32-bit application that sometimes is executed on
        # Windows 64-bit, executing C:\Windows\system32\shutdown.exe is
        # redirected to C:\Windows\SysWOW64\shutdown.exe. The later doesn't
        # exist and we get a "file not found" error. The solution is to
        # disable redirection before executing the shutdown command and
        # re-enable redirection once we're done.
        old_value = c_void_p()
        try:
            windll.kernel32.Wow64DisableWow64FsRedirection(byref(old_value))
        except AttributeError:
            # The function doesn't exist on 32-bit Windows so exeception is
            # ignored.
            pass

        subprocess.call(cmd)

        # Calling this function with the old value received from the first
        # call re-enable the file system redirection.
        if old_value:
            windll.kernel32.Wow64DisableWow64FsRedirection(old_value)

    def hibernate(self, state):
        token = win32security.OpenProcessToken(win32api.GetCurrentProcess(),
            win32security.TOKEN_QUERY | win32security.TOKEN_ADJUST_PRIVILEGES)
        shutdown_priv = win32security.LookupPrivilegeValue(None,
            win32security.SE_SHUTDOWN_NAME)
        privs = win32security.AdjustTokenPrivileges(token, False,
            [ (shutdown_priv, win32security.SE_PRIVILEGE_ENABLED) ])
        logging.debug("Privileges before hibernation: %s", privs)
        if windll.powrprof.SetSuspendState(state=='disk', True, False) != 0:
            logging.info("System was in hibernation state.")
        else:
            logging.error("Error setting system to hibernation state: %d",
                win32api.GetLastError())

    # The LockWorkStation function is callable only by processes running on the interactive desktop.
    def LockWorkStation(self):
        try:
            logging.debug("LockWorkStation was called.")
            sessionId = win32ts.WTSGetActiveConsoleSessionId()
            if sessionId != 0xffffffff:
                logging.debug("Locking workstation (session %d)", sessionId)
                dupToken = None
                userToken = win32ts.WTSQueryUserToken(sessionId)
                if userToken is not None:
                    logging.debug("Got the active user token.")
                    # The following access rights are required for CreateProcessAsUser.
                    access = win32security.TOKEN_QUERY|win32security.TOKEN_DUPLICATE|win32security.TOKEN_ASSIGN_PRIMARY
                    dupToken = win32security.DuplicateTokenEx(userToken, win32security.SecurityImpersonation, access, win32security.TokenPrimary, None)
                    userToken.Close()
                if dupToken is not None:
                    logging.debug("Duplicated the active user token.")
                    lockCmd = "%s\\system32\\rundll32.exe user32.dll,LockWorkStation" % (os.environ['WINDIR'])
                    logging.debug("Executing \"%s\".", lockCmd)
                    win32process.CreateProcessAsUser(dupToken, None, lockCmd, None, None, 0, 0, None, None, win32process.STARTUPINFO())
                    dupToken.Close()
            else:
                logging.debug("No active session. Ignoring lock workstation command.")
        except:
            logging.exception("LockWorkStation exception")

class WinDataRetriver(DataRetriverBase):
    def __init__(self):
        self.os = WinOsTypeHandler().getWinOsType()
        DataRetriverBase.__init__(self)

    def getMachineName(self):
        return os.environ.get('COMPUTERNAME', '')

    def getOsVersion(self):
        return self.os

    def getAllNetworkInterfaces(self):
        return GetNetworkInterfaces()

    def getApplications(self):
        retval = []
        key_path = "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall"
        rootkey = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_path)
        items = _winreg.QueryInfoKey(rootkey)[0]
        for idx in range(items):
            cur_key_path = _winreg.EnumKey(rootkey, idx)
            cur_key = _winreg.OpenKey(rootkey, cur_key_path)
            try:
                cur_key_value = QueryStringValue(cur_key, u"DisplayName")
                if len(cur_key_value) == 0:
                    continue
                if cur_key_value.find("Hotfix") >= 0:
                    continue
                if cur_key_value.find("Security Update") >= 0:
                    continue
                if cur_key_value.find("Update for Windows") >= 0:
                    continue
                retval.append(cur_key_value)
            except:
                pass
        return retval

    def getAvailableRAM(self):
        ## Returns the available physical memory (including the system cache).
        pi = get_perf_info()
        return str(int((pi.PhysicalAvailable * pi.PageSize) / (1024**2)))

    def getUsers(self):
        total_list=[]
        try:
            server = self.getMachineName()
            res = 1  # initially set it to true
            pref = win32netcon.MAX_PREFERRED_LENGTH
            level = 1 # setting it to 1 will provide more detailed info
            while res: # loop until res2
                (user_list,total,res2)=win32net.NetWkstaUserEnum(server,level,res,pref)
                logging.debug("getUsers: user_list = '%s'", user_list)
                for i in user_list:
                    if not i['username'].startswith(server):
                        total_list.append([i['username'],i['logon_domain']])
                res=res2
        except win32net.error:
            logging.exception("WinDataRetriver::getUsers")
        logging.debug("WinDataRetriver::getUsers retval = '%s'", total_list)
        return total_list

    def getActiveUser(self):
        user = "None"
        try:
            domain = ""
            sessionId = win32ts.WTSGetActiveConsoleSessionId()
            if sessionId != 0xffffffff:
                user = win32ts.WTSQuerySessionInformation(win32ts.WTS_CURRENT_SERVER_HANDLE,
                    sessionId, win32ts.WTSUserName)
                domain = win32ts.WTSQuerySessionInformation(win32ts.WTS_CURRENT_SERVER_HANDLE,
                    sessionId, win32ts.WTSDomainName)
            if domain == "":
                pass
            elif domain.lower() != self.getMachineName().lower():
                # Use FQDN as user name if computer is part of a domain.
                try:
                    user = u"%s\\%s" % (domain, user)
                    user = win32security.TranslateName(user,
                        win32api.NameSamCompatible, win32api.NameUserPrincipal)
                    # Check for error because no exception is raised when running under Windows XP.
                    err = win32api.GetLastError()
                    if err != 0:
                        raise RuntimeError(err, 'TranslateName')
                except:
                    logging.exception("Error on user name translation.")
            else:
                user = u"%s@%s" % (user, domain)
        except:
            logging.exception("Error retrieving active user name.")
        logging.debug("Activer user: %s", user)
        return user.encode('utf8')

    def getDisksUsage(self):
        usages = list()
        try:
            drives_mask = win32api.GetLogicalDrives()
            path = 'a'
            while drives_mask > 0:
                path_name = path + ':\\'
                if (drives_mask & 1):
                    try:
                        (free, total) = win32api.GetDiskFreeSpaceEx(path_name)[:2]
                        fs = win32api.GetVolumeInformation(path_name)[4]
                        used = total - free
                        usages.append({ 'path' : path_name, 'fs' : fs, 'total' : total, 'used' : used })
                    except:
                        pass
                drives_mask >>= 1
                path = chr(ord(path) + 1)
        except:
            logging.exception("Error retrieving disks usages.")
        return usages

    def getMemoryStats(self):
        pi = get_perf_info()
        # keep the unit consistent with Linux guests
        self.memStats['mem_total'] = str(int((pi.PhysicalTotal * pi.PageSize) / 1024))
        self.memStats['mem_free'] = str(int((pi.PhysicalAvailable * pi.PageSize) / 1024))
        self.memStats['mem_unused'] = self.memStats['mem_free']
        try:
            strComputer = "."
            objWMIService = win32com.client.Dispatch("WbemScripting.SWbemLocator")
            objSWbemServices = objWMIService.ConnectServer(strComputer, "root\cimv2")
            colItems = objSWbemServices.ExecQuery("SELECT * FROM Win32_PerfFormattedData_PerfOS_Memory")
            for objItem in colItems:
                # Please see the definition of Win32_PerfFormattedData_PerfOS_Memory class in MSDN manual
                # for the explanations of the following fields.
                self.memStats['swap_in'] = objItem.PagesInputPersec
                self.memStats['swap_out'] = objItem.PagesOutputPersec
                self.memStats['pageflt'] = objItem.PageFaultsPersec
                self.memStats['majflt'] = objItem.PageReadsPersec
        except:
            logging.exception("Error retrieving detailed memory stats")
        return self.memStats

class WinVdsAgent(AgentLogicBase):

    def __init__(self, config):
        AgentLogicBase.__init__(self, config)
        self.dr = WinDataRetriver()
        self.commandHandler = CommandHandlerWin()

    def run(self):
        logging.debug("WinVdsAgent:: run() entered")
        try:
            self.disable_screen_saver()
            AgentLogicBase.run(self)
        except:
            logging.exception("WinVdsAgent::run")

    def doWork(self):
        # CoInitialize() should be called in multi-threading program according to msdn document.
        pythoncom.CoInitialize()
        AgentLogicBase.doWork(self)

    def disable_screen_saver(self):
        keyHandle = win32api.RegOpenKeyEx(win32con.HKEY_USERS, ".DEFAULT\Control Panel\Desktop", 0, win32con.KEY_WRITE)
        win32api.RegSetValueEx(keyHandle, "ScreenSaveActive", 0, win32con.REG_SZ, "0")
        keyHandle.Close()

def test():
    dr = WinDataRetriver()
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
