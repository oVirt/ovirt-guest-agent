if INSTALL_USERMODE_SCRIPTS
pamdir = $(PAM_PREFIX)/pam.d
pam_DATA =             \
    ovirt-shutdown     \
    ovirt-logout       \
    ovirt-locksession  \
    ovirt-hibernate    \
    $(NULL)
endif

EXTRA_DIST =           \
    ovirt-shutdown     \
    ovirt-logout       \
    ovirt-locksession  \
    ovirt-hibernate    \
    $(NULL)

CLEANFILES = \
    *~

MAINTAINERCLEANFILES = \
    Makefile.in
