/* pam_ovirt_cred module */

#include "config.h"

#include <stdlib.h>

#define PAM_SM_AUTH

#include <security/_pam_macros.h>
#include <security/pam_modules.h>
#include <security/pam_ext.h>

extern int acquire_user_credentials(const char *ticket,
                                     char **username,
                                     char **password);

PAM_EXTERN int
pam_sm_authenticate(pam_handle_t *pamh, int flags,
                    int argc, const char **argv)
{
    const char *ticket = NULL;
    char *username = NULL;
    char *password = NULL;
    int retval;

    D(("called."));

    /* I'm not too familiar with PAM conversation, so I use the pam_get_user
       function in order to get the ticket that will be send when acquiring
       the user's credentials. */
    retval = pam_get_user(pamh, &ticket, "Token?");
    if (retval != PAM_SUCCESS) {
        D(("get user returned error: %s", pam_strerror(pamh, retval)));
        goto cleanup;
    }
    
    if (acquire_user_credentials(ticket, &username, &password) != 0) {
        D(("failed to acquire user's credentials"));
        retval = PAM_USER_UNKNOWN;
        goto cleanup;
    }

    retval = pam_set_item(pamh, PAM_USER, (const void *) username);
	if (retval != PAM_SUCCESS) {
        D(("username not set: %s", pam_strerror(pamh, retval)));
	    retval = PAM_USER_UNKNOWN;
        goto cleanup;
    }

    retval = pam_set_item(pamh, PAM_AUTHTOK, (const void *) password);
	if (retval != PAM_SUCCESS) {
        D(("password not set: %s", pam_strerror(pamh, retval)));
	    retval = PAM_USER_UNKNOWN;
        goto cleanup;
    }
    
    retval = PAM_SUCCESS;

cleanup:

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
