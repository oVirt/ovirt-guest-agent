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
import subprocess
from OVirtAgentLogic import AgentLogicBase, DataRetriverBase
from ctypes import *
from ctypes.util import find_library
from ctypes.wintypes import *
from IPHelper import GetNetworkInterfaces
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

## Returns the available physical memory (including the system cache).
def MemPerformanceMonitor():
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

    pi = get_perf_info()
    return str(int((pi.PhysicalAvailable * pi.PageSize) / (1024**2)))

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
    WIN7       = 'Win 7'
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
        '3.1.0'  : WINCE3_1_0,
        '3.2.0'  : WINCE3_2_0,
        '3.2.1'  : WINCE3_2_1 ,
        '3.3.0'  : WINCE3_3_0}
    def getWinOsType(self):

        retval = self.UNKNOWN
        try:
            versionTupple = win32api.GetVersionEx(1)
            key = "%d.%d.%d"%(versionTupple[3], versionTupple[0], versionTupple[1])
            if self.winVersionMatrix.has_key(key):
                retval = self.winVersionMatrix[key]
            # Window 7 and Window Server 2008 R2 share the same version.
            # Need to fix it using the wProductType field.
            if retval == WinOsTypeHandler.WIN2008R2:
                VER_NT_WORKSTATION = 1
                if versionTupple[8] == VER_NT_WORKSTATION:
                    retval = WinOsTypeHandler.WIN7
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
        sessionId = self.WTSGetActiveConsoleSessionId()
        if sessionId is not None:
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

    # WTSGetActiveConsoleSessionId is not implemented. Do the console search yourself.
    def WTSGetActiveConsoleSessionId(self):
        sessionId = None
        try:
            sessions = win32ts.WTSEnumerateSessions(win32ts.WTS_CURRENT_SERVER_HANDLE, 1)
            for session in sessions:
                if session['WinStationName'] == u'Console':
                    sessionId = session['SessionId']
                    break
        except:
            logging.exception("WTSGetActiveConsoleSessionId exception")
        return sessionId

    # The LockWorkStation function is callable only by processes running on the interactive desktop.
    def LockWorkStation(self):
        try:
            logging.debug("LockWorkStation was called.")
            sessionId = self.WTSGetActiveConsoleSessionId()
            if sessionId is not None:
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
        return MemPerformanceMonitor()

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
        retval = "None"
        try:
            cur_session = None
            sessionDict = win32ts.WTSEnumerateSessions(win32ts.WTS_CURRENT_SERVER_HANDLE, 1)
            for sess in sessionDict:
                #check if session state is active (=0)
                if sess['State'] == 0:
                    cur_session = sess
                    break
            if cur_session:
                sessionId = cur_session['SessionId']
                userName = win32ts.WTSQuerySessionInformation(win32ts.WTS_CURRENT_SERVER_HANDLE, sessionId, win32ts.WTSUserName)
                domainName = win32ts.WTSQuerySessionInformation(win32ts.WTS_CURRENT_SERVER_HANDLE, sessionId, win32ts.WTSDomainName)
                retval = [userName, domainName]
        except:
            logging.exception("WinDataRetriver::getActiveUser")

        #handling the fqdn
        if type(retval) == types.ListType and len(retval) == 2:
            if retval[1].lower() != self.getMachineName().lower():
                try:
                    translated = win32security.TranslateName(u"%s\\%s" % (retval[1], retval[0]), win32api.NameSamCompatible, win32api.NameUserPrincipal)
                    # Check for error because no exception is thrown when running under Windows XP.
                    err = win32api.GetLastError()
                    if err != 0:
                        raise Exception(err)
                    retval = translated
                except Exception, ex:
                    logging.debug("WinDataRetriver::getActiveUser TranslateName error = '%d'", ex.args[0])
                    retval = u"%s\\%s" % (retval[1], retval[0])
            else:
                retval = u"%s@%s" % (retval[0], retval[1])

        logging.debug("WinDataRetriver::getActiveUser activeUser = '%s'", retval)
        return retval.encode('utf8')

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

if __name__ == '__main__':
    test()
