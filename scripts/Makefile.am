#
# Copyright 2014 Red Hat, Inc. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Refer to the README and COPYING files for full details of the license.
#

SUBDIRS =        \
    diskmapper   \
    wrappers     \
    $(NULL)

osinfoscriptdir = $(pkgdatadir)
osinfoscript_SCRIPTS= \
    ovirt-osinfo         \
    $(NULL)

EXTRA_DIST=                    \
    ovirt-osinfo               \
    sudoers.ovirt-guest-agent  \
    $(NULL)

if INSTALL_SUDO_SCRIPTS
install-data-hook:
	$(MKDIR_P) $(DESTDIR)/$(sysconfdir)/sudoers.d
	$(INSTALL) -m 440 sudoers.ovirt-guest-agent $(DESTDIR)/$(sysconfdir)/sudoers.d/50_ovirt-guest-agent
endif
