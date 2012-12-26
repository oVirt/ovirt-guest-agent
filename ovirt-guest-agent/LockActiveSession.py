#!/usr/bin/python
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

import dbus
import logging
import os


def GetActiveSession():
    session = None
    try:
        bus = dbus.SystemBus()
        manager = dbus.Interface(
            bus.get_object(
                'org.freedesktop.ConsoleKit',
                '/org/freedesktop/ConsoleKit/Manager'),
            dbus_interface='org.freedesktop.ConsoleKit.Manager')
        sessions = manager.GetSessions()
        for session_path in sessions:
            s = dbus.Interface(
                bus.get_object(
                    'org.freedesktop.ConsoleKit', session_path),
                dbus_interface='org.freedesktop.ConsoleKit.Session')
            if s.IsActive():
                session = s
    except:
        logging.exception("Error retrieving active session (ignore if running "
                          "on a system without ConsoleKit installed).")
    return session


def GetScreenSaver():
    try:
        bus = dbus.SessionBus()
        screensaver = dbus.Interface(
            bus.get_object(
                'org.freedesktop.ScreenSaver', '/ScreenSaver'),
            dbus_interface='org.freedesktop.ScreenSaver')
    except dbus.DBusException:
        logging.exception("Error retrieving ScreenSaver interface (ignore if "
                          "running on GNOME).")
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
    logging.debug("Process %d terminated (result = %s)", pid, result)

    # If our first try failed, try the GNOME "standard" interface.
    if result[1] != 0:
        session.Lock()


def main():
    session = GetActiveSession()
    if session is not None:
        try:
            LockSession(session)
            logging.info("Session %s should be locked now.", session.GetId())
        except:
            logging.exception("Error while trying to lock session.")
    else:
        logging.error("Error locking session (no active session).")

if __name__ == '__main__':
    main()
