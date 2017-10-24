%global python_windows_version 2.7.14
%global pywin32_py27_version 221

Name:		ovirt-guest-agent-windows
Version:	1.0.14
Release:	1%{?release_suffix}%{?dist}
Summary:	oVirt Guest Agent Service for Windows
License:	ASL 2.0
Source0:	http:///resources.ovirt.org/pub/src/ovirt-guest-agent/ovirt-guest-agent-%{version}.tar.bz2

URL:		http://www.ovirt.org/
BuildArch:	noarch
Packager:	Lev Veyde <lveyde@redhat.com>

BuildRequires:	p7zip
BuildRequires:	py2exe-py2.7 = 0.6.9
BuildRequires:	python-windows = %{python_windows_version}
BuildRequires:	pywin32-py2.7 = %{pywin32_py27_version}
BuildRequires:	wine
BuildRequires:	wget
BuildRequires:  mingw32-gcc-c++
BuildRequires:  mingw64-gcc-c++

%description
oVirt Guest Agent Service executable for Microsoft Windows platform.

%prep
%setup -q -n ovirt-guest-agent-%{version}

%build

pushd windows-credprov
x86_64-w64-mingw32-g++ *.cpp -I . -o oVirtCredentialsProvider64.dll -shared -static-libstdc++ -static-libgcc -lshlwapi -lsecur32 -lole32 -luuid
i686-w64-mingw32-g++ *.cpp -I . -o oVirtCredentialsProvider32.dll -shared -static-libstdc++ -static-libgcc -lshlwapi -lsecur32 -lole32 -luuid
popd

pushd GinaSSO
i686-w64-mingw32-g++ *.cpp -I . -o oVirtGinaSSO.dll -shared -static-libstdc++ -static-libgcc -lshlwapi -lsecur32 -lole32 -luuid -lwsock32 -DUNICODE
popd

# Use this instead of ~/.wine. See wine(1).
export WINEPREFIX=$PWD/wineprefix

wine msiexec /i %{_datadir}/python-windows/python-%{python_windows_version}.msi /qn ADDLOCAL=ALL
export Path="%PATH%;C:\Python27"

7za x %{_datadir}/pywin32-py2.7/pywin32-%{pywin32_py27_version}.win32-py2.7.exe
mv PLATLIB/* $WINEPREFIX/drive_c/Python27/Lib/site-packages/
rmdir PLATLIB
mv SCRIPTS/* $WINEPREFIX/drive_c/Python27/Lib/site-packages/
rmdir SCRIPTS
pushd $WINEPREFIX/drive_c/Python27/Lib/site-packages/
wine python pywin32_postinstall.py -install -silent -quiet
rm -f ./pywin32_postinstall.py
popd

7za x %{_datadir}/py2exe-py2.7/py2exe-0.6.9.win32-py2.7.exe
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
DST=%{buildroot}%{_datadir}/%{name}/
mkdir -p $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/ovirt-guest-agent/dist/*.exe $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/configurations/default.ini $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/configurations/default-logger.ini $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/configurations/ovirt-guest-agent.ini $DST

# SSO Plugins
cp -v %{_builddir}/ovirt-guest-agent-%{version}/GinaSSO/oVirtGinaSSO.dll $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/windows-credprov/oVirtCredentialsProvider32.dll $DST
cp -v %{_builddir}/ovirt-guest-agent-%{version}/windows-credprov/oVirtCredentialsProvider64.dll $DST

%files
%{_datadir}/%{name}

%changelog
* Mon Oct 23 2017 Tomáš Golembiovský <tgolembi@redhat.com> - 1.0.14-1
- New upstream version 1.0.14

* Mon Oct 23 2017 Tomáš Golembiovský <tgolembi@redhat.com> - 1.0.13-3
- Requrires pywin32 version 221 instead of 220

* Tue Oct 10 2017 Sandro Bonazzola <sbonazzo@redhat.com> - 1.0.13-2
- Requires python 2.7.14 instead of 2.7.12

* Tue Dec 06 2016 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.13-1
- New upstream version 1.0.13

* Thu May 19 2016 Vinzenz Feenstra <vfeenstr@redhat.com> - 1.0.12-1
- Updated version 1.0.12

* Tue Oct 20 2015 Yedidyah Bar David <didi@redhat.com> - 1.0.11-2
- dropped "artifacts" from all paths

* Wed Aug 12 2015 Sandro Bonazzola <sbonazzo@redhat.com> - 1.0.11-1
- New upstream version 1.0.11

* Mon Nov 24 2014 Lev Veyde <lveyde@redhat.com> 1.0.10.3-1
- Updated oVirt Guest Agent

* Wed Oct 08 2014 Lev Veyde <lveyde@redhat.com> 1.0.10.2-2
- Small fixes
