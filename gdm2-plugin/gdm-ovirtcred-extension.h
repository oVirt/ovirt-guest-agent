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

#ifndef __GDM_OVIRTCRED_EXTENSION_H
#define __GDM_OVIRTCRED_EXTENSION_H

#include <glib-object.h>
#include "gdm-greeter-extension.h"

G_BEGIN_DECLS

#define GDM_TYPE_OVIRTCRED_EXTENSION (gdm_ovirtcred_extension_get_type ())
#define GDM_OVIRTCRED_EXTENSION(obj) (G_TYPE_CHECK_INSTANCE_CAST ((obj), GDM_TYPE_OVIRTCRED_EXTENSION, GdmOVirtCredExtension))
#define GDM_OVIRTCRED_EXTENSION_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST ((klass), GDM_TYPE_OVIRTCRED_EXTENSION, GdmOVirtCredExtensionClass))
#define GDM_IS_OVIRTCRED_EXTENSION(obj) (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GDM_TYPE_OVIRTCRED_EXTENSION))
#define GDM_IS_OVIRTCRED_EXTENSION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GDM_TYPE_OVIRTCRED_EXTENSION))
#define GDM_OVIRTCRED_EXTENSION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GDM_TYPE_OVIRTCRED_EXTENSION, GdmOVirtCredExtensionClass))

typedef struct _GdmOVirtCredExtensionPrivate GdmOVirtCredExtensionPrivate;

typedef struct
{
        GObject parent;
        GdmOVirtCredExtensionPrivate *priv;

} GdmOVirtCredExtension;

typedef struct
{
        GObjectClass parent_class;

} GdmOVirtCredExtensionClass;

GType                 gdm_ovirtcred_extension_get_type   (void);

GdmOVirtCredExtension *gdm_ovirtcred_extension_new        (void);

G_END_DECLS

#endif /* GDM_OVIRTCRED_EXTENSION_H */
