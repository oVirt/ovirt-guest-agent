
SUBDIRS = icons

NULL =

PAM_SERVICE_NAME = gdm-ovirtcred

extensiondir = $(extensionsdatadir)/ovirtcred
extension_DATA = page.ui

AM_CPPFLAGS = \
	-DPLUGINDATADIR=\""$(extensiondir)"\" \
	-DGDM_OVIRTCRED_EXTENSION_SERVICE_NAME=\""$(PAM_SERVICE_NAME)"\" \
	$(DISABLE_DEPRECATED_CFLAGS) \
	$(GTK_CFLAGS) \
	$(GDM_PLUGIN_CFLAGS) \
	$(POLKIT_GNOME_CFLAGS) \
	$(NULL)

plugindir = $(GDM_SIMPLE_GREETER_PLUGINS_DIR)
plugin_LTLIBRARIES = libovirtcred.la

libovirtcred_la_CFLAGS = $(SIMPLE_GREETER_CFLAGS) -fPIC
libovirtcred_la_LDFLAGS = -module -avoid-version -export-dynamic
libovirtcred_la_LIBADD = $(GDM_PLUGIN_LIBS)
libovirtcred_la_SOURCES = \
	gdm-ovirtcred-extension.h \
	gdm-ovirtcred-extension.c

$(PAM_SERVICE_NAME): $(PAM_SERVICE_NAME).pam
	cp $(PAM_SERVICE_NAME).pam $(PAM_SERVICE_NAME)

pamdir = $(PAM_PREFIX)/pam.d
pam_DATA = $(PAM_SERVICE_NAME)

EXTRA_DIST = $(extension_DATA) $(PAM_SERVICE_NAME).pam

MAINTAINERCLEANFILES = \
	*~ \
	$(PAM_SERVICE_NAME) \
	Makefile.in
