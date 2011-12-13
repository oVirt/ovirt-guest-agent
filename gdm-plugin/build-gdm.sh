#!/bin/sh

GDM=gdm-2.30.4-14.el6.src.rpm

which rpmbuild || {
    echo "You need to install rpmbuild package."
    exit 1
}

rpm -i $GDM

rpmbuild -bc ~/rpmbuild/SPECS/gdm.spec
