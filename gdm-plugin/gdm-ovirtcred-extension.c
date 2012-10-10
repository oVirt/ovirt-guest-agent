/*
 * Copyright (C) 2011 Red Hat, Inc.
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
 * Based on a code written by: Ray Strode <rstrode@redhat.com>
 */

#include <config.h>
#include <stdlib.h>

#include "gdm-ovirtcred-extension.h"

#include <gio/gio.h>
#include <gtk/gtk.h>

#define DBUS_API_SUBJECT_TO_CHANGE
#include <dbus/dbus-glib.h>
#include <dbus/dbus-glib-lowlevel.h>

#define GDM_OVIRTCRED_SERVER_DBUS_NAME      "org.ovirt.vdsm.Credentials"
#define GDM_OVIRTCRED_SERVER_DBUS_PATH      "/org/ovirt/vdsm/Credentials"
#define GDM_OVIRTCRED_SERVER_DBUS_INTERFACE GDM_OVIRTCRED_SERVER_DBUS_NAME

struct _GdmOVirtCredExtensionPrivate
{
        GIcon     *icon;
        GtkWidget *page;
        GtkActionGroup *actions;

        GtkWidget *message_label;

        GQueue    *message_queue;
        guint      message_timeout_id;

        guint      select_when_ready : 1;
        
        DBusGProxy      *cred_proxy;
        DBusGConnection *connection;
        gchar           *token;
};

typedef struct {
        char                  *text;
        GdmServiceMessageType  type;
} QueuedMessage;

static void gdm_ovirtcred_extension_finalize (GObject *object);

static void gdm_login_extension_iface_init (GdmLoginExtensionIface *iface);

G_DEFINE_TYPE_WITH_CODE (GdmOVirtCredExtension,
                         gdm_ovirtcred_extension,
                         G_TYPE_OBJECT,
                         G_IMPLEMENT_INTERFACE (GDM_TYPE_LOGIN_EXTENSION,
                                                gdm_login_extension_iface_init));

static void
on_user_authenticated (DBusGProxy *proxy,
                       gchar      *token,
                       gpointer    user_data)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (user_data);
        
        g_debug ("on_user_authenticated: %s", token);
        
        if (token == NULL) {
                g_warning ("no token");
                return;
        }
        
        extension->priv->token = g_strdup (token);
        if (extension->priv->token == NULL) {
                g_warning ("failed to save token");
                return;
        }
        
        if (!_gdm_login_extension_emit_choose_user (GDM_LOGIN_EXTENSION (extension),
                                                    GDM_OVIRTCRED_EXTENSION_SERVICE_NAME)) {
                g_debug ("failed to choose user, canceling...");
                _gdm_login_extension_emit_cancel (GDM_LOGIN_EXTENSION (extension));
                extension->priv->select_when_ready = TRUE;
        }
}

static void
ovirtcred_server_start (GdmOVirtCredExtension *extension)
{
        GError *error;
        
        g_debug ("Attempting listening to %s D-Bus interface...", GDM_OVIRTCRED_SERVER_DBUS_INTERFACE);

        error = NULL;
        extension->priv->connection = dbus_g_bus_get (DBUS_BUS_SYSTEM, &error);
        if (extension->priv->connection == NULL) {
                if (error != NULL) {
                        g_critical ("Error getting system bus: %s", error->message);
                        g_error_free (error);
                }
        }

        extension->priv->cred_proxy = dbus_g_proxy_new_for_name (extension->priv->connection,
                                                                  GDM_OVIRTCRED_SERVER_DBUS_NAME,
                                                                  GDM_OVIRTCRED_SERVER_DBUS_PATH,
                                                                  GDM_OVIRTCRED_SERVER_DBUS_INTERFACE);
        if (extension->priv->cred_proxy == NULL) {
                g_warning ("error creating proxy");
        }
        
        dbus_g_proxy_add_signal (extension->priv->cred_proxy, "UserAuthenticated",
                                 G_TYPE_STRING,
                                 G_TYPE_INVALID);

        dbus_g_proxy_connect_signal (extension->priv->cred_proxy, "UserAuthenticated",
                                     G_CALLBACK (on_user_authenticated),
                                     extension,
                                     NULL);
}

static void
ovirtcred_server_stop (GdmOVirtCredExtension *extension)
{
        if (extension->priv->cred_proxy != NULL) {
                g_object_unref (extension->priv->cred_proxy);
                extension->priv->cred_proxy = NULL;
        }

        if (extension->priv->connection != NULL) {
                g_object_unref (extension->priv->connection);
                extension->priv->connection = NULL;
        }
}

static void
set_message (GdmOVirtCredExtension *extension,
             const char            *message)
{
        gtk_widget_show (extension->priv->message_label);
        gtk_label_set_text (GTK_LABEL (extension->priv->message_label), message);
}

static void
free_queued_message (QueuedMessage *message)
{
        g_free (message->text);
        g_slice_free (QueuedMessage, message);
}

static void
purge_message_queue (GdmOVirtCredExtension *extension)
{
        if (extension->priv->message_timeout_id) {
                g_source_remove (extension->priv->message_timeout_id);
                extension->priv->message_timeout_id = 0;
        }
        g_queue_foreach (extension->priv->message_queue,
                         (GFunc) free_queued_message,
                         NULL);
        g_queue_clear (extension->priv->message_queue);
}

static gboolean
dequeue_message (GdmOVirtCredExtension *extension)
{
        if (!g_queue_is_empty (extension->priv->message_queue)) {
                int duration;
                gboolean needs_beep;

                QueuedMessage *message;
                message = (QueuedMessage *) g_queue_pop_head (extension->priv->message_queue);

                switch (message->type) {
                        case GDM_SERVICE_MESSAGE_TYPE_INFO:
                                needs_beep = FALSE;
                                break;
                        case GDM_SERVICE_MESSAGE_TYPE_PROBLEM:
                                needs_beep = TRUE;
                                break;
                        default:
                                g_assert_not_reached ();
                }

                set_message (extension, message->text);

                duration = (int) (g_utf8_strlen (message->text, -1) / 66.0) * 1000;
                duration = CLAMP (duration, 400, 3000);

                extension->priv->message_timeout_id = g_timeout_add (duration,
                                                                     (GSourceFunc) dequeue_message,
                                                                     extension);
                if (needs_beep) {
                        gdk_window_beep (gtk_widget_get_window (GTK_WIDGET (extension)));
                }

                free_queued_message (message);
        } else {
                extension->priv->message_timeout_id = 0;

                _gdm_login_extension_emit_message_queue_empty (GDM_LOGIN_EXTENSION (extension));
        }

        return FALSE;
}

static void
gdm_ovirtcred_extension_queue_message (GdmLoginExtension *login_extension,
                                       GdmServiceMessageType type,
                                       const char *text)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);

        QueuedMessage *message = g_slice_new (QueuedMessage);

        message->text = g_strdup (text);
        message->type = type;

        g_queue_push_tail (extension->priv->message_queue, message);

        if (extension->priv->message_timeout_id == 0) {
                dequeue_message (extension);
        }
}

static void
gdm_ovirtcred_extension_ask_question (GdmLoginExtension *login_extension,
                                      const char *message)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);

        if (g_strcmp0 ("Token?", message) != 0) {
                return;
        }

        _gdm_login_extension_emit_answer (login_extension, extension->priv->token);
}

static void
gdm_ovirtcred_extension_ask_secret (GdmLoginExtension *login_extension,
                                    const char *message)
{

}

static void
gdm_ovirtcred_extension_reset (GdmLoginExtension *login_extension)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);
        
        if (extension->priv->token) {
                g_free (extension->priv->token);
                extension->priv->token = NULL;
        }

        set_message (extension, "");
        purge_message_queue (extension);

        gdm_login_extension_set_enabled (login_extension, FALSE);
}

static void
gdm_ovirtcred_extension_set_ready (GdmLoginExtension *login_extension)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);
        
        gdm_login_extension_set_enabled (login_extension, TRUE);

        if (extension->priv->cred_proxy == NULL) {
                ovirtcred_server_start (extension);
        }

        if (extension->priv->select_when_ready) {
                if (_gdm_login_extension_emit_choose_user (login_extension,
                                                           GDM_OVIRTCRED_EXTENSION_SERVICE_NAME)) {
                        extension->priv->select_when_ready = FALSE;
                }
        }
}

static char *
gdm_ovirtcred_extension_get_service_name (GdmLoginExtension *login_extension)
{
        return g_strdup (GDM_OVIRTCRED_EXTENSION_SERVICE_NAME);
}

static GtkWidget *
gdm_ovirtcred_extension_get_page (GdmLoginExtension *login_extension)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);

        return extension->priv->page;
}

static GtkActionGroup *
gdm_ovirtcred_extension_get_actions (GdmLoginExtension *login_extension)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);

        return g_object_ref (extension->priv->actions);
}

static gboolean
gdm_ovirtcred_extension_focus (GdmLoginExtension *login_extension)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);

        gtk_widget_grab_focus (extension->priv->message_label);

        return TRUE;
}

static gboolean
gdm_ovirtcred_extension_has_queued_messages (GdmLoginExtension *login_extension)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);

        if (extension->priv->message_timeout_id != 0) {
                return TRUE;
        }

        if (!g_queue_is_empty (extension->priv->message_queue)) {
                return TRUE;
        }

        return FALSE;
}

static GIcon *
gdm_ovirtcred_extension_get_icon (GdmLoginExtension *login_extension)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (login_extension);

        return g_object_ref (extension->priv->icon);
}

static char *
gdm_ovirtcred_extension_get_name (GdmLoginExtension *extension)
{
        return g_strdup ("OVirtCred Authentication");
}

static char *
gdm_ovirtcred_extension_get_description (GdmLoginExtension *extension)
{
        return g_strdup ("oVirt single-sign-on login");
}

static gboolean
gdm_ovirtcred_extension_is_choosable (GdmLoginExtension *extension)
{
        return TRUE;
}

static gboolean
gdm_ovirtcred_extension_is_visible (GdmLoginExtension *login_extension)
{
        char *contents, *pid_dir;
        pid_t pid;

        if (g_file_get_contents ("/var/run/ovirt-guest-agent.pid",
                                 &contents, NULL, NULL) == FALSE) {
                return FALSE;
        }

        pid = (pid_t) atoi (contents);
        g_free (contents);

        if (pid == 0) {
                return FALSE;
        }

        pid_dir = g_strdup_printf ("/proc/%d", (int) pid);
        if (!g_file_test (pid_dir, G_FILE_TEST_EXISTS)) {
                g_free (pid_dir);
                return FALSE;
        }
        g_free (pid_dir);

        return TRUE;
}

static void
gdm_login_extension_iface_init (GdmLoginExtensionIface *iface)
{
        iface->get_icon = gdm_ovirtcred_extension_get_icon;
        iface->get_description = gdm_ovirtcred_extension_get_description;
        iface->get_name = gdm_ovirtcred_extension_get_name;
        iface->is_choosable = gdm_ovirtcred_extension_is_choosable;
        iface->is_visible = gdm_ovirtcred_extension_is_visible;
        iface->queue_message = gdm_ovirtcred_extension_queue_message;
        iface->ask_question = gdm_ovirtcred_extension_ask_question;
        iface->ask_secret = gdm_ovirtcred_extension_ask_secret;
        iface->reset = gdm_ovirtcred_extension_reset;
        iface->set_ready = gdm_ovirtcred_extension_set_ready;
        iface->get_service_name = gdm_ovirtcred_extension_get_service_name;
        iface->get_page = gdm_ovirtcred_extension_get_page;
        iface->get_actions = gdm_ovirtcred_extension_get_actions;
        iface->focus = gdm_ovirtcred_extension_focus;
        iface->has_queued_messages = gdm_ovirtcred_extension_has_queued_messages;
}

static void
gdm_ovirtcred_extension_class_init (GdmOVirtCredExtensionClass *extension_class)
{
        GObjectClass *object_class = G_OBJECT_CLASS (extension_class);

        object_class->finalize = gdm_ovirtcred_extension_finalize;

        g_type_class_add_private (extension_class,
                                  sizeof (GdmOVirtCredExtensionPrivate));
}

static void
gdm_ovirtcred_extension_finalize (GObject *object)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (object);

        purge_message_queue (extension);

        if (extension->priv->token) {
                g_free (extension->priv->token);
                extension->priv->token = NULL;
        }

        ovirtcred_server_stop (extension);
}

static void
create_page (GdmOVirtCredExtension *extension)
{
        GtkBuilder *builder;
        GObject *object;
        GError *error;

        builder = gtk_builder_new ();

        error = NULL;
        gtk_builder_add_from_file (builder,
                                   PLUGINDATADIR "/page.ui",
                                   &error);

        if (error != NULL) {
                g_warning ("Could not load UI file: %s", error->message);
                g_error_free (error);
                return;
        }

        object = gtk_builder_get_object (builder, "page");
        g_object_ref (object);

        extension->priv->page = GTK_WIDGET (object);

        object = gtk_builder_get_object (builder, "auth-message-label");
        g_object_ref (object);
        extension->priv->message_label = GTK_WIDGET (object);
        gtk_widget_show (extension->priv->message_label);

        g_object_unref (builder);
}

static void
create_actions (GdmOVirtCredExtension *extension)
{
        extension->priv->actions = gtk_action_group_new (GDM_OVIRTCRED_EXTENSION_NAME);
}

static void
gdm_ovirtcred_extension_init (GdmOVirtCredExtension *extension)
{
        extension->priv = G_TYPE_INSTANCE_GET_PRIVATE (extension,
                                                       GDM_TYPE_OVIRTCRED_EXTENSION,
                                                       GdmOVirtCredExtensionPrivate);

        extension->priv->icon = g_themed_icon_new ("gdm-ovirtcred");
        create_page (extension);
        create_actions (extension);

        extension->priv->message_queue = g_queue_new ();

        gdm_ovirtcred_extension_reset (GDM_LOGIN_EXTENSION (extension));
}

void
g_io_module_load (GIOModule *module)
{
        g_io_extension_point_implement (GDM_LOGIN_EXTENSION_POINT_NAME,
                                        GDM_TYPE_OVIRTCRED_EXTENSION,
                                        GDM_OVIRTCRED_EXTENSION_NAME,
                                        0);
}

void
g_io_module_unload (GIOModule *module)
{

}
