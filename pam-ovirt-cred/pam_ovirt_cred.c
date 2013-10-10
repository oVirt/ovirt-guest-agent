/* pam_ovirt_cred module */

#include "config.h"

#include <stdlib.h>
#include <syslog.h>

#define PAM_SM_AUTH

#include <security/_pam_macros.h>
#include <security/pam_modules.h>
#include <security/pam_ext.h>

extern int acquire_user_credentials(const char *token,
                                    char **username,
                                    char **password);

PAM_EXTERN int
pam_sm_authenticate(pam_handle_t *pamh, int flags,
                    int argc, const char **argv)
{
    char *token = NULL;
    const char * preset_user = NULL;
    char *username = NULL;
    char *password = NULL;
    int retval;

    D(("called."));

    /* Request the authentication token via pam conversation */
    retval = pam_prompt(pamh, PAM_PROMPT_ECHO_OFF, &token, "Token?");
    if(retval != PAM_SUCCESS) {
        pam_syslog(pamh, LOG_ERR, "Failed to retrieve auth token: %s",
                   pam_strerror(pamh, retval));
        retval = PAM_USER_UNKNOWN;
        goto cleanup;
    }

    /* The conversation succeeded but we have retrieved an invalid value */
    if (token == NULL) {
        pam_syslog(pamh, LOG_ERR, "Conversation result is an invalid token");
        retval = PAM_USER_UNKNOWN;
        goto cleanup;
    }

    /* Retrieve the user credentials from the guest agent service */
    if (acquire_user_credentials(token, &username, &password) != 0) {
        pam_syslog(pamh, LOG_ERR, "Failed to acquire user's credentials");
        retval = PAM_USER_UNKNOWN;
        goto cleanup;
    }

    /* Ensure that the username retrieved and the preset user name are
     * identical, in case the username was provided
     * We don't want to unlock a screen which was locked for a different
     * user.
     */
    retval = pam_get_item(pamh, PAM_USER, (void const **)&preset_user);
    if (retval == PAM_SUCCESS) {
        if(username && preset_user) {
            if(strcmp(username, preset_user) != 0) {
                pam_syslog(pamh, LOG_ERR, "Preset user [%s] is not the same"
                           "as the retrieved user [%s]", preset_user,
                           username);
                retval = PAM_CRED_UNAVAIL;
                goto cleanup;
            }
        }
    }

    /* Hand the username over to PAM */
    retval = pam_set_item(pamh, PAM_USER, (const void *) username);
    if (retval != PAM_SUCCESS) {
        pam_syslog(pamh, LOG_ERR, "Username not set: %s",
                   pam_strerror(pamh, retval));
        goto cleanup;
    }

    /* Hand the password over to PAM */
    retval = pam_set_item(pamh, PAM_AUTHTOK, (const void *) password);
    if (retval != PAM_SUCCESS) {
        pam_syslog(pamh, LOG_ERR, "Password not set: %s",
                   pam_strerror(pamh, retval));
        goto cleanup;
    }

    retval = PAM_SUCCESS;

cleanup:
    /* We have to cleanup the token we have retrieved via the conversation */
    if (token) {
        free(token);
    }
    _pam_overwrite(password);
    _pam_drop(password);
    _pam_drop(username);

    return retval;
}

PAM_EXTERN int
pam_sm_setcred(pam_handle_t *pamh, int flags,
               int argc, const char **argv)
{
    return PAM_SUCCESS;
}

#ifdef PAM_STATIC

struct pam_module _pam_unix_auth_modstruct = {
    "pam_ovirt_cred",
    pam_sm_authenticate,
    pam_sm_setcred,
    NULL,
    NULL,
    NULL,
    NULL,
};

#endif /* PAM_STATIC */
