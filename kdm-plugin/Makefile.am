
PAM_SERVICE_NAME = kdm-ovirtcred

dist_noinst_DATA =              \
    src/CMakeLists.txt          \
    src/kgreet_ovirtcred.h      \
    src/kgreet_ovirtcred.cpp    \
    src/OVirtCred.h             \
    src/OVirtCred.cpp

kgreet_ovirtcreddir = $(KDM_GREETER_PLUGINS_DIR)
kgreet_ovirtcred_DATA = kgreet_ovirtcred.so

kgreet_ovirtcred.so:
	cmake -DCMAKE_INSTALL_PREFIX=/usr src/CMakeLists.txt
	make -C src
	(	TMPDIR=`mktemp -d`; \
		DESTDIR=$$TMPDIR make -C src install; \
		install -s $$TMPDIR/$(KDM_GREETER_PLUGINS_DIR)/kgreet_ovirtcred.so .; \
		rm -rf $$TMPDIR )

$(PAM_SERVICE_NAME): $(PAM_SERVICE_NAME).pam
	cp $(PAM_SERVICE_NAME).pam $(PAM_SERVICE_NAME)

pamdir = $(PAM_PREFIX)/pam.d
pam_DATA = $(PAM_SERVICE_NAME)

EXTRA_DIST = $(PAM_SERVICE_NAME).pam

CLEANFILES =            \
    *~                  \
    kgreet_ovirtcred.so  \
    $(PAM_SERVICE_NAME)
