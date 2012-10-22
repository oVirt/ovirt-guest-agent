
PAM_SERVICE_NAME = kdm-ovirtcred

dist_noinst_DATA =              \
    src/CMakeLists.txt          \
    src/kgreet_ovirtcred.h      \
    src/kgreet_ovirtcred.cpp    \
    src/OVirtCred.h             \
    src/OVirtCred.cpp

all-local:
	cmake -DCMAKE_INSTALL_PREFIX=/usr src/CMakeLists.txt
	make -C src

clean-local:
	make -C src clean

install-exec-hook:
	make -C src install DESTDIR=$(DESTDIR)

$(PAM_SERVICE_NAME): $(PAM_SERVICE_NAME).pam
	cp $(PAM_SERVICE_NAME).pam $(PAM_SERVICE_NAME)

pamdir = $(PAM_PREFIX)/pam.d
pam_DATA = $(PAM_SERVICE_NAME)

EXTRA_DIST = $(PAM_SERVICE_NAME).pam

CLEANFILES =            \
    *~                  \
    $(PAM_SERVICE_NAME)
