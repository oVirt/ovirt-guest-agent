
%global release_version 1

Name: ovirt-guest-agent
Version: 1.0.7
Release: %{release_version}%{?dist}
Summary: The oVirt Guest Agent
Group: Applications/System
License: ASL 2.0
URL: http://wiki.ovirt.org/wiki/Category:Ovirt_guest_agent
Source0: http://ovirt.org/releases/stable/src/%{name}-%{version}.tar.bz2
BuildArch: noarch
BuildRequires: python2-devel
Requires: dbus-python
Requires: rpm-python
Requires: python-ethtool >= 0.4-1
Requires: udev >= 095-14.23
Requires: kernel > 2.6.18-238.5.0
Requires: usermode

Conflicts: rhev-agent
Conflicts: rhevm-guest-agent
Conflicts: rhevm-guest-agent-common
%if 0%{?rhel} <= 6
Conflicts: selinux-policy < 3.7.19-188
%endif

%description
This is the oVirt management agent running inside the guest. The agent
interfaces with the oVirt manager, supplying heart-beat info as well as
run-time data from within the guest itself. The agent also accepts
control commands to be run executed within the OS (like: shutdown and
restart).

%prep
%setup -q -n ovirt-guest-agent-%{version}

%build
%configure \
    --includedir=%{_includedir}/security \
    --without-sso

make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

%if 0%{?rhel}
    # Install SystemV init script.
    install -Dm 0755 ovirt-guest-agent/ovirt-guest-agent %{buildroot}%{_initrddir}/ovirt-guest-agent
%endif

%pre
getent group ovirtagent >/dev/null || groupadd -r -g 175 ovirtagent
getent passwd ovirtagent > /dev/null || \
    /usr/sbin/useradd -u 175 -g 175 -o -r ovirtagent \
    -c "oVirt Guest Agent" -d %{_datadir}/ovirt-guest-agent -s /sbin/nologin
exit 0

%post
/sbin/chkconfig --add ovirt-guest-agent

%posttrans
/sbin/udevadm trigger --subsystem-match="virtio-ports" \
    --attr-match="name=com.redhat.rhevm.vdsm"

%preun
if [ "$1" -eq 0 ]
then
    /sbin/service ovirt-guest-agent stop > /dev/null 2>&1
    /sbin/chkconfig --del ovirt-guest-agent

    # Send an "uninstalled" notification to vdsm.
    VIRTIO=`grep "^device" %{_sysconfdir}/ovirt-guest-agent.conf | awk '{ print $3; }'`
    if [ -w $VIRTIO ]
    then
        # Non blocking uninstalled notification
        echo -e '{"__name__": "uninstalled"}\n' | dd of=$VIRTIO \
            oflag=nonblock status=noxfer conv=nocreat 1>& /dev/null || :
    fi
fi

%postun
if [ "$1" -eq 0 ]
then
    # Let udev clear access rights
    /sbin/udevadm trigger --subsystem-match="virtio-ports" \
        --attr-match="name=com.redhat.rhevm.vdsm"
fi

if [ "$1" -ge 1 ]; then
    /sbin/service ovirt-guest-agent condrestart > /dev/null 2>&1
fi

%files
%dir %attr (755,ovirtagent,ovirtagent) %{_localstatedir}/log/ovirt-guest-agent
%dir %attr (755,root,root) %{_datadir}/ovirt-guest-agent

%config(noreplace) %{_sysconfdir}/ovirt-guest-agent.conf

%doc AUTHORS COPYING NEWS README

# These are intentionally NOT 'noreplace' If this is modified by an user,
# this actually might break it.
%config(noreplace) %{_sysconfdir}/pam.d/ovirt-locksession
%config(noreplace) %{_sysconfdir}/pam.d/ovirt-shutdown
%config(noreplace) %{_sysconfdir}/pam.d/ovirt-hibernate
%config(noreplace) %attr (644,root,root) %{_sysconfdir}/udev/rules.d/55-ovirt-guest-agent.rules
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/org.ovirt.vdsm.Credentials.conf
%config(noreplace) %{_sysconfdir}/security/console.apps/ovirt-locksession
%config(noreplace) %{_sysconfdir}/security/console.apps/ovirt-shutdown
%config(noreplace) %{_sysconfdir}/security/console.apps/ovirt-hibernate

%attr (755,root,root) %{_datadir}/ovirt-guest-agent/ovirt-guest-agent.py*

%{_datadir}/ovirt-guest-agent/OVirtAgentLogic.py*
%{_datadir}/ovirt-guest-agent/VirtIoChannel.py*
%{_datadir}/ovirt-guest-agent/CredServer.py*
%{_datadir}/ovirt-guest-agent/GuestAgentLinux2.py*
%{_datadir}/ovirt-guest-agent/ovirt-locksession
%{_datadir}/ovirt-guest-agent/ovirt-shutdown
%{_datadir}/ovirt-guest-agent/ovirt-hibernate

%attr (755,root,root) %{_datadir}/ovirt-guest-agent/LockActiveSession.py*
%attr (755,root,root) %{_datadir}/ovirt-guest-agent/hibernate

%attr (755,root,root) %{_initrddir}/ovirt-guest-agent


%changelog
* Wed Jul 10 2013 Vinzenz Feenstra <evilissimo@redhat.com> - 1.0.7-1
  - Initial ovirt-guest-agent RHEL6 package
