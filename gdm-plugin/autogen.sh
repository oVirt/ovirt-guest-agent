#!/bin/sh

REQUIRED_AUTOMAKE_VERSION=1.5
USE_GNOME2_MACROS=1

srcdir=`dirname $0`
test -z "$srcdir" && srcdir=.

PKG_NAME="gdm-plugin-rhevcred"

(test -f $srcdir/configure.ac ) || {
    echo -n "***Error***: Directory "\`$srcdir\'" does not look like the"
    echo " top-level gdm-plugin-rhevcred directory."
    exit 1
}

which gnome-autogen.sh || {
    echo "You need to install gnome-common package."
    exit 1
}

. gnome-autogen.sh
