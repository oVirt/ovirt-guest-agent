Name:		ovirt-guest-agent-windows
Version:	1.0.11
Release:	1%{?release_suffix}
Summary:	oVirt Guest Agent Service for Windows
License:	ASL 2.0
Source0:	https://evilissimo.fedorapeople.org/releases/ovirt-guest-agent/1.0.11/ovirt-guest-agent-%{version}.tar.bz2

URL:		http://www.ovirt.org/
BuildArch:	noarch
Packager:	Lev Veyde <lveyde@redhat.com>

BuildRequires:	p7zip
BuildRequires:	py2exe-py2.7 = 0.6.9
BuildRequires:	python-windows = 2.7.8
BuildRequires:	pywin32-py2.7 = 219
BuildRequires:	wine
BuildRequires:	wget

%description
oVirt Guest Agent Service executable for Microsoft Windows platform.

%prep
%setup -q -n ovirt-guest-agent-%{version}

%build
# Use this instead of ~/.wine. See wine(1).
export WINEPREFIX=$PWD/wineprefix

wine msiexec /i %{_datadir}/artifacts/python-windows/python-2.7.8.msi /qn ADDLOCAL=ALL
export Path="%PATH%;C:\Python27"

7za x %{_datadir}/artifacts/pywin32-py2.7/pywin32-219.win32-py2.7.exe
mv PLATLIB/* $WINEPREFIX/drive_c/Python27/Lib/site-packages/
rmdir PLATLIB
mv SCRIPTS/* $WINEPREFIX/drive_c/Python27/Lib/site-packages/
rmdir SCRIPTS
pushd $WINEPREFIX/drive_c/Python27/Lib/site-packages/
wine python pywin32_postinstall.py -install -silent -quiet
rm -f ./pywin32_postinstall.py
popd

7za x %{_datadir}/artifacts/py2exe-py2.7/py2exe-0.6.9.win32-py2.7.exe
mv PLATLIB/* $WINEPREFIX/drive_c/Python27/Lib/site-packages/
rmdir PLATLIB
mv SCRIPTS/* $WINEPREFIX/drive_c/Python27/Lib/site-packages/
rmdir SCRIPTS
pushd $WINEPREFIX/drive_c/Python27/Lib/site-packages/
wine python ./py2exe_postinstall.py -install
rm -f ./py2exe_postinstall.py
popd

pushd ovirt-guest-agent
mkdir -p build/bdist.win32/winexe/bundle-2.7/
cp  $WINEPREFIX/drive_c/Python27/python27.dll build/bdist.win32/winexe/bundle-2.7/
wine cmd.exe /C win-guest-agent-build-exe.bat
popd

%install
DST=%{buildroot}%{_datadir}/artifacts/%{name}/
mkdir -p $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/ovirt-guest-agent/dist/*.exe $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/configurations/default.ini $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/configurations/default-logger.ini $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/configurations/ovirt-guest-agent.ini $DST

%files
%{_datadir}/artifacts/%{name}

%changelog
* Wed Aug 12 2015 Sandro Bonazzola <sbonazzo@redhat.com> - 1.0.11-1
- New upstream version 1.0.11

* Mon Nov 24 2014 Lev Veyde <lveyde@redhat.com> 1.0.10.3-1
- Updated oVirt Guest Agent

* Wed Oct 08 2014 Lev Veyde <lveyde@redhat.com> 1.0.10.2-2
- Small fixes
