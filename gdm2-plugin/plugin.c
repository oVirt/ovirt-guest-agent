/*
 * Copyright (C) 2010-2012 Red Hat, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Refer to the README and COPYING files for full details of the license.
 *
 * Written By: Gal Hammer <ghammer@redhat.com>
 * Base on code written by: Ray Strode <rstrode@redhat.com>
 *
 */

#include "gdm-ovirtcred-extension.h"

#include <gio/gio.h>
#include <gtk/gtk.h>

GdmGreeterExtension *
gdm_greeter_plugin_get_extension (void)
{
        static GObject *extension;

        if (extension != NULL) {
                g_object_ref (extension);
        } else {
                extension = g_object_new (GDM_TYPE_OVIRTCRED_EXTENSION, NULL);
                g_object_add_weak_pointer (extension, (gpointer *) &extension);
        }

        return GDM_GREETER_EXTENSION (extension);
}
