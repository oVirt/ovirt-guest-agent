
%global release_version 1

%global _moduledir /%{_lib}/security
%global _kdmrc /etc/kde/kdm/kdmrc

Name: ovirt-guest-agent
Version: 1.0.11
Release: %{release_version}%{?release_suffix}%{?dist}
Summary: The oVirt Guest Agent
Group: Applications/System
License: ASL 2.0
URL: http://wiki.ovirt.org/wiki/Category:Ovirt_guest_agent
Source0: https://evilissimo.fedorapeople.org/releases/ovirt-guest-agent/1.0.11/%{name}-%{version}.tar.bz2
BuildRequires: libtool
BuildRequires: pam-devel
BuildRequires: python2-devel
%if 0%{?fedora} >= 18
BuildRequires: systemd
%else
BuildRequires: systemd-units
%endif
Requires: %{name}-common = %{version}-%{release}

%package common
Summary: Commonly used files of the oVirt Guest Agent
BuildArch: noarch
BuildRequires: python-pep8
Requires: dbus-python
Requires: rpm-python
Requires: qemu-guest-agent
Requires: python-ethtool >= 0.4-1
Requires: udev >= 095-14.23
Requires: kernel > 2.6.18-238.5.0
Requires: usermode
Provides: %{name} = %{version}-%{release}

%if 0%{?fc16}
Conflicts: selinux-policy < 3.10.0-77
%endif
%if 0%{?fedora} >= 17
Conflicts: selinux-policy < 3.10.0-89
%endif

%package pam-module
Summary: PAM module for the oVirt Guest Agent
Requires: %{name} = %{version}-%{release}
Requires: pam

%if 0%{?fedora} < 19
%package gdm-plugin
Summary: GDM plug-in for the oVirt Guest Agent
BuildRequires: dbus-glib-devel
BuildRequires: gdm-devel
BuildRequires: gobject-introspection-devel
BuildRequires: gtk2-devel
Requires: %{name} = %{version}-%{release}
Requires: %{name}-pam-module = %{version}-%{release}
Requires: gdm
%endif

%package kdm-plugin
Summary: KDM plug-in for the oVirt Guest Agent
BuildRequires: kdebase-workspace-devel
BuildRequires: gcc-c++
Requires: %{name} = %{version}-%{release}
Requires: %{name}-pam-module = %{version}-%{release}
Requires: kdm

%description
This is the oVirt management agent running inside the guest. The agent
interfaces with the oVirt manager, supplying heart-beat info as well as
run-time data from within the guest itself. The agent also accepts
control commands to be run executed within the OS (like: shutdown and
restart).

%description common
This is the oVirt management agent running inside the guest. The agent
interfaces with the oVirt manager, supplying heart-beat info as well as
run-time data from within the guest itself. The agent also accepts
control commands to be run executed within the OS (like: shutdown and
restart).

%description pam-module
The oVirt PAM module provides the functionality necessary to use the
oVirt automatic log-in system.

%if 0%{?fedora} < 19
%description gdm-plugin
The GDM plug-in provides the functionality necessary to use the
oVirt automatic log-in system.
%endif

%description kdm-plugin
The KDM plug-in provides the functionality necessary to use the
oVirt automatic log-in system.

%prep
%setup -q -n ovirt-guest-agent-%{version}

%build
%configure \
    --enable-securedir=%{_moduledir} \
    --includedir=%{_includedir}/security \
%if 0%{?fedora} >= 19
    --without-gdm \
%endif
    --with-pam-prefix=%{_sysconfdir}

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

%pre common
getent group ovirtagent >/dev/null || groupadd -r -g 175 ovirtagent
getent passwd ovirtagent > /dev/null || \
    /usr/sbin/useradd -u 175 -g 175 -o -r ovirtagent \
    -c "oVirt Guest Agent" -d %{_datadir}/ovirt-guest-agent -s /sbin/nologin
exit 0

%post common
/sbin/udevadm trigger --subsystem-match="virtio-ports" \
    --attr-match="name=com.redhat.rhevm.vdsm"

/bin/systemctl daemon-reload

%post kdm-plugin
if ! grep -q "^PluginsLogin=" "%{_kdmrc}";
then
    sed -i "s~^#PluginsLogin=winbind~PluginsLogin=ovirtcred,classic~" "%{_kdmrc}"
fi

%preun common
if [ "$1" -eq 0 ]
then
    /bin/systemctl stop ovirt-guest-agent.service > /dev/null 2>&1

    # Send an "uninstalled" notification to vdsm.
    VIRTIO=`grep "^device" %{_sysconfdir}/ovirt-guest-agent.conf | awk '{ print $3; }'`
    if [ -w $VIRTIO ]
    then
        # Non blocking uninstalled notification
        echo -e '{"__name__": "uninstalled"}\n' | dd of=$VIRTIO \
            oflag=nonblock status=noxfer conv=nocreat 1>& /dev/null || :
    fi
fi

%postun common
if [ "$1" -eq 0 ]
then
    /bin/systemctl daemon-reload
    # Let udev clear access rights
    /sbin/udevadm trigger --subsystem-match="virtio-ports" \
        --attr-match="name=com.redhat.rhevm.vdsm"
fi

if [ "$1" -ge 1 ]; then
    /bin/systemctl try-restart ovirt-guest-agent.service >/dev/null 2>&1 || :
fi

%postun kdm-plugin
if [ "$1" -eq 0 ]
then
    sed -i "s~PluginsLogin=ovirtcred,classic~#PluginsLogin=winbind~" "%{_kdmrc}"
fi

%files common
%dir %attr (755,ovirtagent,ovirtagent) %{_localstatedir}/log/ovirt-guest-agent
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent

# Hook configuration directories
%dir %attr (755,root,root) %{_sysconfdir}/ovirt-guest-agent
%dir %attr (755,root,root) %{_sysconfdir}/ovirt-guest-agent/hooks.d
%dir %attr (755,root,root) %{_sysconfdir}/ovirt-guest-agent/hooks.d/before_migration
%dir %attr (755,root,root) %{_sysconfdir}/ovirt-guest-agent/hooks.d/after_migration
%dir %attr (755,root,root) %{_sysconfdir}/ovirt-guest-agent/hooks.d/before_hibernation
%dir %attr (755,root,root) %{_sysconfdir}/ovirt-guest-agent/hooks.d/after_hibernation

# Hook installation directories
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent/scripts
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent/scripts/hooks/
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent/scripts/hooks/defaults
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent/scripts/hooks/before_migration
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent/scripts/hooks/after_migration
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent/scripts/hooks/before_hibernation
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent/scripts/hooks/after_hibernation

%config(noreplace) %{_sysconfdir}/ovirt-guest-agent.conf

%doc AUTHORS COPYING NEWS README

# These are intentionally NOT 'noreplace' If this is modified by an user,
# this actually might break it.
%config %{_sysconfdir}/pam.d/ovirt-logout
%config %{_sysconfdir}/pam.d/ovirt-locksession
%config %{_sysconfdir}/pam.d/ovirt-shutdown
%config %{_sysconfdir}/pam.d/ovirt-hibernate
%config %attr (644,root,root) %{_sysconfdir}/udev/rules.d/55-ovirt-guest-agent.rules
%config %{_sysconfdir}/dbus-1/system.d/org.ovirt.vdsm.Credentials.conf
%config %{_sysconfdir}/security/console.apps/ovirt-logout
%config %{_sysconfdir}/security/console.apps/ovirt-locksession
%config %{_sysconfdir}/security/console.apps/ovirt-shutdown
%config %{_sysconfdir}/security/console.apps/ovirt-hibernate

%attr (755,root,root) %{_datadir}/ovirt-guest-agent/ovirt-guest-agent.py*

%{_datadir}/ovirt-guest-agent/OVirtAgentLogic.py*
%{_datadir}/ovirt-guest-agent/VirtIoChannel.py*
%{_datadir}/ovirt-guest-agent/CredServer.py*
%{_datadir}/ovirt-guest-agent/GuestAgentLinux2.py*
%{_datadir}/ovirt-guest-agent/hooks.py*
%{_datadir}/ovirt-guest-agent/timezone.py*
%{_datadir}/ovirt-guest-agent/ovirt-osinfo
%{_datadir}/ovirt-guest-agent/ovirt-logout

# consolehelper symlinks
%{_datadir}/ovirt-guest-agent/ovirt-locksession
%{_datadir}/ovirt-guest-agent/ovirt-shutdown
%{_datadir}/ovirt-guest-agent/ovirt-hibernate

%attr (755,root,root) %{_datadir}/ovirt-guest-agent/LockActiveSession.py*
%attr (755,root,root) %{_datadir}/ovirt-guest-agent/LogoutActiveUser.py*
%attr (755,root,root) %{_datadir}/ovirt-guest-agent/hibernate

%attr (644,root,root) %{_datadir}/ovirt-guest-agent/default.conf
%attr (644,root,root) %{_datadir}/ovirt-guest-agent/default-logger.conf
%attr (755,root,root) %{_datadir}/ovirt-guest-agent/diskmapper

%{_unitdir}/ovirt-guest-agent.service

%files pam-module
%{_moduledir}/pam_ovirt_cred.so
%exclude %{_moduledir}/pam_ovirt_cred.a
%exclude %{_moduledir}/pam_ovirt_cred.la

%if 0%{?fedora} < 19
%files gdm-plugin
# This is intentionally NOT 'noreplace' If this is modified by an user,
# this actually might break it.
%config %{_sysconfdir}/pam.d/gdm-ovirtcred
%{_datadir}/icons/hicolor/*/*/*.png
%dir %{_datadir}/gdm/simple-greeter/extensions/ovirtcred
%{_datadir}/gdm/simple-greeter/extensions/ovirtcred/page.ui
%{_libdir}/gdm/simple-greeter/extensions/libovirtcred.so
# Unwanted files
%exclude %{_libdir}/gdm/simple-greeter/extensions/libovirtcred.a
%exclude %{_libdir}/gdm/simple-greeter/extensions/libovirtcred.la
%endif

%files kdm-plugin
%config %{_sysconfdir}/pam.d/kdm-ovirtcred
%attr (755,root,root) %{_libdir}/kde4/kgreet_ovirtcred.so

%changelog
* Mon Jul 20 2015 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.11-1
- New upstream version 1.0.11

* Tue Feb 10 2015 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.10-2
- Adding ovirt-osinfo script

* Tue Jul 01 2014 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.10-1
- New upstream version 1.0.10

* Mon Jan 20 2014 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.9-1
- Report swap usage of guests
- Updated pam conversation approach
- Python 2.4 compatability fix
- Some build fixes applied

* Thu Jul 11 2013 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.8-1
- Pep8 rules applied on python files
- Call restorecon on pidfile
- Report multiple IPv4 addresses per device if available
- Send 'uninstalled' notification non blocking
- fixed "modified" files after clone.
- rewrote nic's addresses functions in python 2.4 syntax.
- GNOME 3.8 no longer supports gdm plugins. Therefore it's now disabled for
  higher versions
- Added full qualified domain name reporting
- Condrestart now ensures that the pid file does not only exist, but also is
  not empty
- Added new optional parameter for shutdown to allow reboot

* Tue Dec 25 2012 Gal Hammer <ghammer@redhat.com> - 1.0.7-1
- reset user rights on virtio-channel during package removal.
- unification of line endings to unix.
- fixed support for reporting devices with only ipv6.
- fixed pep8 errors in the linux guest agent.

* Wed Dec 05 2012 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.6-1
- New upstream version 1.0.6
- Upstream build system is now taking care of folder creation
- Upstream build system is now taking care of systemd units installation

* Wed Nov 28 2012 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.5-3
- License has been changed to Apache Software License 2.0

* Fri Oct 19 2012 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.5-2
- introduced ovirt-guest-agent-common noarch package which provides
  ovirt-guest-agent and avoids duplication of the same package content
- fixed various rpmlint errors and warnings
- added required build requires
- removed unnecessary build requires
- removed unnecessary call to autoreconf in setup section
- marked config files as such
- excluded unwanted files instead of deleting them
- removed consolehelper based symlinks - now in upstream make install

* Sun May 20 2012 Gal Hammer <ghammer@redhat.com> - 1.0.5-1
- fixed 'udevadm trigger' command line (bz#819945).
- fixed various rpmlint errors and warnings.

* Tue May 15 2012 Gal Hammer <ghammer@redhat.com> - 1.0.4-1
- replaced "with" usage with a python 2.4 compatible way.
- added files to support RHEL-5 distribution.
- added more detailed memory statistics.
- fixed build on fc-17 (use the _unitdir macro).

* Sun Apr 15 2012 Gal Hammer <ghammer@redhat.com> - 1.0.3-2
- removed the RHEL distribution support for the review process.
- removed BuildRoot header and clean section.
- fixed user creation.

* Tue Apr 10 2012 Gal Hammer <ghammer@redhat.com> - 1.0.3-1
- package was renamed to rhevm-guest-agent in RHEL distribution.
- fixed gdm-plugin build requires.
Resolves: BZ#803503

* Wed Mar 28 2012 Gal Hammer <ghammer@redhat.com> - 1.0.2-1
- included a gpl-v2 copying file.
- build the gdm-plugin using the gdm-devel package.
- added a support for RHEL distribution.

* Wed Feb 22 2012 Gal Hammer <ghammer@redhat.com> - 1.0.1-2
- updated required selinux-policy version (related to rhbz#791113).
- added a support to hibernate (s4) command.
- renamed user name to ovirtguest.
- reset version numbering after changing the package name.

* Tue Sep 27 2011 Gal Hammer <ghammer@redhat.com> - 2.3.15-1
- fixed disk usage report when mount point include spaces.
- added a minimum version for python-ethtool.
Resolves: BZ#736426

* Thu Sep 22 2011 Gal Hammer <ghammer@redhat.com> - 2.3.14-1
- added a new 'echo' command to support testing.
Resolves: BZ#736426

* Thu Sep 15 2011 Gal Hammer <ghammer@redhat.com> - 2.3.13-1
- report new network interaces information (ipv4, ipv6 and
  mac address).
- added disks usage report.
- a new json-based protocol with the vdsm.
Resolves: BZ#729252 BZ#736426

* Mon Aug  8 2011 Gal Hammer <ghammer@redhat.com> - 2.3.12-1
- replaced password masking with a fixed-length string.
Resolves: BZ#727506

* Thu Aug  4 2011 Gal Hammer <ghammer@redhat.com> - 2.3.11-1
- send an 'uninstalled' notification to vdsm
- mask the user's password in the credentials block
Resolves: BZ#727647 BZ#727506

* Mon Aug  1 2011 Gal Hammer <ghammer@redhat.com> - 2.3.10-2
- fixed selinux-policy required version.
Resolves: BZ#694088

* Mon Jul 25 2011 Gal Hammer <ghammer@redhat.com> - 2.3.10-1
- various fixes after failing the errata's rpmdiff.
- added selinux-policy dependency.
Resolves: BZ#720144 BZ#694088

* Thu Jun 16 2011 Gal Hammer <ghammer@redhat.com> - 2.3.9-1
- read report rate values from configuration file.
- replaced executing privilege commands from sudo to
  consolehelper.
Resolves: BZ#713079 BZ#632959

* Tue Jun 14 2011 Gal Hammer <ghammer@redhat.com> - 2.3.8-1
- execute the agent with a non-root user.
- changed the shutdown timeout value to work in minutes.
- update pam config files to work with selinux.
- fixed the local user check when stripping the domain part.
Resolves: BZ#632959 BZ#711428 BZ#694088 BZ#661713 BZ#681123

* Wed May 25 2011 Gal Hammer <ghammer@redhat.com> - 2.3.7-1
- stopped removing the domain part from the user name.
- show only network interfaces that are up and running.
Resolves: BZ#661713 BZ#681123 BZ#704845

* Mon Apr 4 2011 Gal Hammer <ghammer@redhat.com> - 2.3.6-1
- added kdm greeter plug-in.
Resolves: BZ#681123

* Mon Mar 14 2011 Gal Hammer <ghammer@redhat.com> - 2.3.5-1
- replaced rhevcredserver execution from blocking main loop to
  context's iteration (non-blocking).
Resolves: BZ#683493

* Thu Mar 10 2011 Gal Hammer <ghammer@redhat.com> - 2.3.4-1
- added some sleep-ing to init script in order to give udev
  some time to create the symbolic links.
- changed the kernel version condition.
Resolves: BZ#676625 BZ#681527

* Wed Mar 2 2011 Gal Hammer <ghammer@redhat.com> - 2.3.3-1
- removed unused file (rhevcredserver) from rhel-5 build.
- added udev and kernel minimum version requirment.
- fixed pid file location in spec file.
Resolves: BZ#681524 BZ#681527 BZ#681533

* Tue Mar 1 2011 Gal Hammer <ghammer@redhat.com> - 2.3.2-1
- updated the agent's makefile to work with auto-tools.
- added sub packages to support the single-sign-on feature.
- added -h parameter to shutdown command in order to halt the vm
  after shutdown.
- converted configuration file to have unix-style line ending.
- added redhat-rpm-config to build requirements in order to
  include *.pyc and *.pyo in the rpm file.
Resolves: BZ#680107 BZ#661713 BZ#679470 BZ#679451

* Wed Jan 19 2011 Gal Hammer <ghammer@redhat.com> - 2.3-7
- fixed files' mode to include execution flag.
Resolves: BZ#670476

* Mon Jan 17 2011 Gal Hammer <ghammer@redhat.com> - 2.3-6
- fixed the way the exit code was returned. the script always
  return 0 (success) because the main program ended and errors
  from the child process were lost.
Resolves: BZ#658092

* Thu Dec 23 2010 Gal Hammer <ghammer@redhat.com> - 2.3-5
- added description to startup/shutdown script in order to support
  chkconfig.
- a temporary fix to the 100% cpu usage when the vdsm doesn't
  listen to the virtio-serial.
Resolves: BZ#639702

* Sun Dec 19 2010 Gal Hammer <ghammer@redhat.com> - 2.3-4
- BZ#641886: lock command now handle both gnome and kde.
Resolves: BZ#641886

* Tue Dec 07 2010 Barak Azulay <bazulay@redhat.com> - 2.3-3
- BZ#660343 load virtio_console module before starting the daemon.
- BZ#660231 register daemon for startup.
Resolves: BZ#660343 BZ#660231

* Sun Dec 05 2010 Barak Azulay <bazulay@redhat.com> - 2.3-2
- initial build for RHEL-6
- works over vioserial
- Agent reports only heartbeats, IPs, app list
- performs: shutdown & lock (the lock works only on gnome - when
  ConsoleKit & gnome-screensaver is installed)
Resolves: BZ#613059

* Fri Aug 27 2010 Gal Hammer <ghammer@redhat.com> - 2.3-1
- Initial build.
