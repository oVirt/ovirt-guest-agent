#!/usr/bin/python
#
# Copyright 2010 Red Hat, Inc. and/or its affiliates.
#
# Licensed to you under the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.  See the files README and
# LICENSE_GPL_v2 which accompany this distribution.
#

import dbus, logging, os

def GetActiveSession():
    session = None
    try:
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object('org.freedesktop.ConsoleKit',
            '/org/freedesktop/ConsoleKit/Manager'),
            dbus_interface='org.freedesktop.ConsoleKit.Manager')
        sessions = manager.GetSessions()
        for session_path in sessions:
            s = dbus.Interface(bus.get_object('org.freedesktop.ConsoleKit', session_path),
                dbus_interface='org.freedesktop.ConsoleKit.Session')
            if s.IsActive():
                session = s
    except:
        logging.exception("Error retrieving active session (ignore if running on a system without ConsoleKit installed).")
    return session

def GetScreenSaver():
    try:
        bus = dbus.SessionBus()
        screensaver = dbus.Interface(bus.get_object('org.freedesktop.ScreenSaver', '/ScreenSaver'),
            dbus_interface='org.freedesktop.ScreenSaver')
    except dbus.DBusException:
        logging.exception("Error retrieving ScreenSaver interface (ignore if running on GNOME).")
        screensaver = None
    return screensaver

def LockSession(session):
    # First try to lock in the KDE "standard" interface. Since KDE is
    # using a session bus, all operations must be execued in the user
    # context.
    pid = os.fork()
    if pid == 0:
        os.environ['DISPLAY'] = session.GetX11Display()
        os.setuid(session.GetUnixUser())
        screensaver = GetScreenSaver()
        if screensaver is not None:
            screensaver.Lock()
            exitcode = 0
        else:
            exitcode = 1
        os._exit(exitcode)
        
    result = os.waitpid(pid, 0)
    logging.debug("Process %d terminated (result = %s)" % (pid, result))
    
    # If our first try failed, try the GNOME "standard" interface.
    if result[1] != 0:
       session.Lock()

def main():
    session = GetActiveSession()
    if session is not None:
        try:
            LockSession(session)
            logging.info("Session %s should be locked now." % (session.GetId()))
        except:
            logging.exception("Error while trying to lock session.")
    else:
        logging.error("Error locking session (no active session).")

if __name__ == '__main__':
    main()
