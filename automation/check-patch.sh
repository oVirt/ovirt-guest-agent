#!/bin/bash -xe

./autogen.sh
./configure \
    --prefix=/usr \
    --exec_prefix=/usr \
    --sysconfdir=/etc \
    --localstatedir=/var \
    --without-sso
make check
