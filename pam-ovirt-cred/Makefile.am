
AM_CFLAGS = -I$(top_srcdir) -Wall -pedantic
AM_LDFLAGS = -no-undefined -avoid-version -module

securelibdir = $(SECUREDIR)
securelib_LTLIBRARIES = pam_ovirt_cred.la

pam_ovirt_cred_la_CFLAGS=-fPIC
pam_ovirt_cred_la_LIBADD = -lpam
pam_ovirt_cred_la_SOURCES =  \
			pam_ovirt_cred.c	\
			cred_channel.c

CLEANFILES = *~
