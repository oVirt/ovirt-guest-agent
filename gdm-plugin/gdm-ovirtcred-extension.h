/*
 * Copyright (C) 2010 Red Hat, Inc.
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 * Written By: Gal Hammer <ghammer@redhat.com>
 * Base on code written by: Ray Strode <rstrode@redhat.com>
 *
 */

#ifndef __GDM_RHEVCRED_EXTENSION_H
#define __GDM_RHEVCRED_EXTENSION_H

#include <glib-object.h>
#include "gdm-greeter-extension.h"

G_BEGIN_DECLS

#define GDM_TYPE_RHEVCRED_EXTENSION (gdm_rhevcred_extension_get_type ())
#define GDM_RHEVCRED_EXTENSION(obj) (G_TYPE_CHECK_INSTANCE_CAST ((obj), GDM_TYPE_RHEVCRED_EXTENSION, GdmRhevCredExtension))
#define GDM_RHEVCRED_EXTENSION_CLASS(klass) (G_TYPE_CHECK_CLASS_CAST ((klass), GDM_TYPE_RHEVCRED_EXTENSION, GdmRhevCredExtensionClass))
#define GDM_IS_RHEVCRED_EXTENSION(obj) (G_TYPE_CHECK_INSTANCE_TYPE ((obj), GDM_TYPE_RHEVCRED_EXTENSION))
#define GDM_IS_RHEVCRED_EXTENSION_CLASS(klass) (G_TYPE_CHECK_CLASS_TYPE ((klass), GDM_TYPE_RHEVCRED_EXTENSION))
#define GDM_RHEVCRED_EXTENSION_GET_CLASS(obj)  (G_TYPE_INSTANCE_GET_CLASS((obj), GDM_TYPE_RHEVCRED_EXTENSION, GdmRhevCredExtensionClass))

typedef struct _GdmRhevCredExtensionPrivate GdmRhevCredExtensionPrivate;

typedef struct
{
        GObject parent;
        GdmRhevCredExtensionPrivate *priv;

} GdmRhevCredExtension;

typedef struct
{
        GObjectClass parent_class;

} GdmRhevCredExtensionClass;

GType                 gdm_rhevcred_extension_get_type   (void);

GdmRhevCredExtension *gdm_rhevcred_extension_new        (void);

G_END_DECLS

#endif /* GDM_RHEVCRED_EXTENSION_H */
