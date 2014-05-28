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

#include <config.h>

#include "gdm-ovirtcred-extension.h"
#include "gdm-conversation.h"
#include "gdm-task.h"

#include <stdlib.h>

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
        GIcon           *icon;
        GtkWidget       *page;
        GtkActionGroup  *actions;

        GtkWidget       *message_label;
        guint            message_timeout_id;

        guint            select_when_ready : 1;

        DBusGProxy      *cred_proxy;
        DBusGConnection *connection;
        gchar           *token;
};

static void gdm_ovirtcred_extension_finalize (GObject *object);

static void gdm_task_iface_init (GdmTaskIface *iface);
static void gdm_conversation_iface_init (GdmConversationIface *iface);
static void gdm_greeter_extension_iface_init (GdmGreeterExtensionIface *iface);

void gdm_ovirtcred_extension_request_answer (GdmConversation *conversation);

G_DEFINE_TYPE_WITH_CODE (GdmOVirtCredExtension,
                         gdm_ovirtcred_extension,
                         G_TYPE_OBJECT,
                         G_IMPLEMENT_INTERFACE (GDM_TYPE_GREETER_EXTENSION,
                                                gdm_greeter_extension_iface_init)
                         G_IMPLEMENT_INTERFACE (GDM_TYPE_TASK,
                                                gdm_task_iface_init)
                         G_IMPLEMENT_INTERFACE (GDM_TYPE_CONVERSATION,
                                                gdm_conversation_iface_init));

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
    
        if (!gdm_conversation_choose_user (GDM_CONVERSATION (extension), PAMSERVICENAME)) {
                g_debug ("failed to choose user, canceling...");
                gdm_conversation_cancel (GDM_CONVERSATION (extension));
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

static gboolean
on_message_expired (GdmConversation *conversation)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);
        
        extension->priv->message_timeout_id = 0;
        gdm_conversation_message_set (conversation);

        return FALSE;
}

static void
gdm_ovirtcred_extension_set_message (GdmConversation *conversation,
                                    const char      *message)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);

        gtk_widget_show (extension->priv->message_label);
        gtk_label_set_text (GTK_LABEL (extension->priv->message_label), message);

        if (extension->priv->message_timeout_id  != 0) {
                g_source_remove (extension->priv->message_timeout_id);
        }

        extension->priv->message_timeout_id = g_timeout_add_seconds (2, (GSourceFunc) on_message_expired, conversation);
}

static void
gdm_ovirtcred_extension_ask_question (GdmConversation *conversation,
                                     const char      *message)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);
        
        if (g_strcmp0 ("Token?", message) != 0) {
                return;
        }
        
        if (extension->priv->token) {
                gdm_ovirtcred_extension_request_answer (GDM_CONVERSATION (extension));
        }
}

static void
gdm_ovirtcred_extension_ask_secret (GdmConversation *conversation,
                                   const char      *message)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);
        
        if (g_strcmp0 ("Token?", message) != 0) {
                return;
        }
        
        if (extension->priv->token) {
                gdm_ovirtcred_extension_request_answer (GDM_CONVERSATION (extension));
        }
}

static void
gdm_ovirtcred_extension_reset (GdmConversation *conversation)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);

        if (extension->priv->token) {
                g_free (extension->priv->token);
                extension->priv->token = NULL;
        }

        gdm_task_set_enabled (GDM_TASK (conversation), FALSE);
}

static void
gdm_ovirtcred_extension_set_ready (GdmConversation *conversation)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);
        
        gdm_task_set_enabled (GDM_TASK (conversation), TRUE);

        if (extension->priv->cred_proxy == NULL) {
                ovirtcred_server_start (extension);
        }

        if (extension->priv->select_when_ready) {
                if (gdm_conversation_choose_user (GDM_CONVERSATION (extension),
                                                  PAMSERVICENAME)) {
                        extension->priv->select_when_ready = FALSE;
                }
        }
}

char *
gdm_ovirtcred_extension_get_service_name (GdmConversation *conversation)
{
        return g_strdup (PAMSERVICENAME);
}

GtkWidget *
gdm_ovirtcred_extension_get_page (GdmConversation *conversation)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);

        return extension->priv->page;
}

GtkActionGroup *
gdm_ovirtcred_extension_get_actions (GdmConversation *conversation)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);

        return g_object_ref (extension->priv->actions);
}

void
gdm_ovirtcred_extension_request_answer (GdmConversation *conversation)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);
        
        g_debug ("gdm_ovirtcred_extension_request_answer");

        if (extension->priv->token == NULL) {
                gdm_conversation_answer (conversation, NULL);
                return;
        }

        gdm_conversation_answer (conversation, extension->priv->token);

        g_free(extension->priv->token);
        extension->priv->token = NULL;
}

gboolean
gdm_ovirtcred_extension_focus (GdmConversation *conversation)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (conversation);

        gtk_widget_grab_focus (extension->priv->message_label);
        return TRUE;
}

GIcon *
gdm_ovirtcred_extension_get_icon (GdmTask *task)
{
        GdmOVirtCredExtension *extension = GDM_OVIRTCRED_EXTENSION (task);

        return g_object_ref (extension->priv->icon);
}

char *
gdm_ovirtcred_extension_get_name (GdmTask *task)
{
        return g_strdup ("OVIRT-M Authentication");
}

char *
gdm_ovirtcred_extension_get_description (GdmTask *task)
{
        return g_strdup ("OVIRT-M Single-Sign-On Login");
}

gboolean
gdm_ovirtcred_extension_is_choosable (GdmTask *task)
{
        return TRUE;
}

gboolean
gdm_ovirtcred_extension_is_visible (GdmTask *task)
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
gdm_task_iface_init (GdmTaskIface *iface)
{
        iface->get_icon = gdm_ovirtcred_extension_get_icon;
        iface->get_description = gdm_ovirtcred_extension_get_description;
        iface->get_name = gdm_ovirtcred_extension_get_name;
        iface->is_choosable = gdm_ovirtcred_extension_is_choosable;
        iface->is_visible = gdm_ovirtcred_extension_is_visible;
}

static void
gdm_conversation_iface_init (GdmConversationIface *iface)
{
        iface->set_message = gdm_ovirtcred_extension_set_message;
        iface->ask_question = gdm_ovirtcred_extension_ask_question;
        iface->ask_secret = gdm_ovirtcred_extension_ask_secret;
        iface->reset = gdm_ovirtcred_extension_reset;
        iface->set_ready = gdm_ovirtcred_extension_set_ready;
        iface->get_service_name = gdm_ovirtcred_extension_get_service_name;
        iface->get_page = gdm_ovirtcred_extension_get_page;
        iface->get_actions = gdm_ovirtcred_extension_get_actions;
        iface->request_answer = gdm_ovirtcred_extension_request_answer;
        iface->focus = gdm_ovirtcred_extension_focus;
}

static void
gdm_greeter_extension_iface_init (GdmGreeterExtensionIface *iface)
{

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

        if (extension->priv->token) {
                g_free (extension->priv->token);
                extension->priv->token = NULL;
        }

        ovirtcred_server_stop (extension);
        g_source_remove (extension->priv->message_timeout_id);
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
        gtk_widget_hide (extension->priv->message_label);

        g_object_unref (builder);
}

static void
create_actions (GdmOVirtCredExtension *extension)
{
        /* It seems that the greeter doesn't like plugins without actions. */
        extension->priv->actions = gtk_action_group_new ("gdm-ovirtcred-extension");
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
        gdm_ovirtcred_extension_reset (GDM_CONVERSATION (extension));
}
