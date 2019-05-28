#!/bin/bash -xe

# cleanup leftovers from previous builds
rm -rf exported-artifacts
rm -rf tmp.repos

mkdir -p exported-artifacts
mkdir -p tmp.repos

if git describe --exact-match --tags --match "[0-9]*" > /dev/null 2>&1 ; then
    SUFFIX=""
else
    SUFFIX=".$(date -u +%Y%m%d%H%M%S).git$(git rev-parse --short HEAD)"
fi

./autogen.sh
./configure \
    --with-dist
make dist

if ! rpm --eval "%dist" | grep -qFi 'el6'; then
    yum-builddep -y ovirt-guest-agent-windows.spec
    rpmbuild \
        -D "_topdir $PWD/tmp.repos" \
        -D "_sourcedir $PWD" \
        ${SUFFIX:+-D "release_suffix ${SUFFIX}"} \
        -ba ovirt-guest-agent-windows.spec
fi

if rpm --eval "%dist" | grep -qFi 'el6'; then
    yum-builddep -y ovirt-guest-agent.rhel6.spec
    rpmbuild \
        -D "_topdir $PWD/tmp.repos" \
        -D "_sourcedir $PWD" \
        ${SUFFIX:+-D "release_suffix ${SUFFIX}"} \
        -ba ovirt-guest-agent.rhel6.spec
fi

if rpm --eval "%dist" | grep -qFi 'el7'; then
    yum-builddep -y ovirt-guest-agent.spec
    rpmbuild \
        -D "_topdir $PWD/tmp.repos" \
        -D "_sourcedir $PWD" \
        ${SUFFIX:+-D "release_suffix ${SUFFIX}"} \
        -ba ovirt-guest-agent.spec
fi

mv *.tar.bz2 exported-artifacts
find \
    "$PWD/tmp.repos" \
    -iname \*.rpm \
    -exec mv {} exported-artifacts/ \;
