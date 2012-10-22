ACLOCAL_AMFLAGS=-I m4

SUBDIRS =                \
    ovirt-guest-agent    \
    pam-ovirt-cred       \
    gdm-plugin           \
    gdm2-plugin          \
    kdm-plugin

CLEANFILES = \
    *~

MAINTAINERCLEANFILES = \
    config.h.in \
    Makefile.in

install-exec-hook:
	$(MKDIR_P) $(DESTDIR)/$(pkgdatadir)
	$(LN_S) $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-locksession
	$(LN_S) $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-shutdown
	$(LN_S) $(bindir)/consolehelper $(DESTDIR)/$(pkgdatadir)/ovirt-hibernate
	$(INSTALL) -d $(DESTDIR)/$(localstatedir)/lock/subsys/ovirt-guest-agent
	$(INSTALL) -d $(DESTDIR)/$(localstatedir)/log/ovirt-guest-agent
