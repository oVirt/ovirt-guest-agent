/*
 * Copyright (C) 2011 Red Hat, Inc.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2, or (at your option)
 * any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; If not, see <http://www.gnu.org/licenses/>.
 *
 * Written By: Gal Hammer <ghammer@redhat.com>
 * Based on a code written by: Ray Strode <rstrode@redhat.com>
 */

#ifndef __GDM_OVIRTCRED_EXTENSION_H
#define __GDM_OVIRTCRED_EXTENSION_H

#include <glib-object.h>
#include "gdm-login-extension.h"

G_BEGIN_DECLS

#define GDM_TYPE_OVIRTCRED_EXTENSION (gdm_ovirtcred_extension_get_type ())
#define GDM_OVIRTCRED_EXTENSION(obj) (G_TYPE_CHECK_INSTANCE_CAST ((obj), GDM_TYPE_OVIRTCRED_EXTENSION, GdmOVirtCredExtension))
#define GDM_OVIRTCRED_EXTENSION_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST ((klass), GDM_TYPE_OVIRTCRED_EXTENSION, GdmOVirtCredExtensionClass))
#define GDM_IS_OVIRTCRED_EXTENSION(obj) (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GDM_TYPE_OVIRTCRED_EXTENSION))
#define GDM_IS_OVIRTCRED_EXTENSION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GDM_TYPE_OVIRTCRED_EXTENSION))
#define GDM_OVIRTCRED_EXTENSION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GDM_TYPE_OVIRTCRED_EXTENSION, GdmOVirtCredExtensionClass))

#define GDM_OVIRTCRED_EXTENSION_NAME "gdm-ovirtcred-extension"

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

GType                 gdm_ovirtcred_extension_get_type      (void);

G_END_DECLS

#endif /* GDM_OVIRTCRED_EXTENSION_H */
