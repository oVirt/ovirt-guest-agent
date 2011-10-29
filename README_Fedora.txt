Ovirt Guest Agent for Fedora - setting up dev env & building the rpms
=====================================================================
NOTE:
- In order to build on Fedora  you may need to use rpmdevtools 
- there are still some sub rpms that do not compile properly in Fedora 15 
  (gdm & kdm plugins) so there are still lot's of commented lines in the 
  configure.ac & spec file. These issues will be resolved soon.
- was tested on Fedora 15.



Getting started
---------------
git clone <ovirt-guest-agent repo>
cd ovirt-guest-agent
./autogen.sh
./configure

Building sources
----------------
make

Installing locally
------------------
sudo make install


Building rpms
------------- 
make dist

rpmbuild -bb --define="_sourcedir <PATH_TO_SRC_TAR>" ovirt-guest-agent.spec

you may skip --define="_sourcedir if you used rpmdevtools to setup your env
