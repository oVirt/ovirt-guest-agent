
#include "config.h"

#include <arpa/inet.h>
#include <sys/un.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <pwd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <security/_pam_macros.h>

#define CREDENTIAL_CHANNEL  "x/tmp/ovirt-cred-channel"

static int parse_credentials_buffer(const char *creds,
                                     size_t len,
                                     char **username,
                                     char **password)
{
    char *domain;
    int user_len, pass_len;

    if (len < sizeof(int)) {
        return -1;
    }

    user_len = ntohl(*((int *)creds));
    *username = strndup(creds + sizeof(int), user_len);
    if (*username == NULL) {
            return -1;
    }

    pass_len = len - sizeof(int) - user_len;
    *password = strndup(creds + sizeof(int) + user_len, pass_len);
    if (*password == NULL) {
            _pam_drop(*username);
            return -1;
    }
    
    domain = strchr(*username, '@');
    if (domain != NULL) {
        *domain = '\0';
        /* local/nis users doesn't have a domain. */
        if (getpwnam(*username) == NULL) {
            *domain = '@';
        } else {
            domain += 1;
        }
    }

    return 0;
}

static int set_sock_non_blocking(int sock)
{
    int flags;

    if ((flags = fcntl(sock, F_GETFL)) == -1) {
        D(("fcntl(F_GETFL) failed."));
        return -1;
    }

    if (fcntl(sock, F_SETFL, flags | O_NONBLOCK) == -1) {
        D(("fcntl(F_SETFL, O_NONBLOCK) failed."));
        return -1;
    }

    return 0;
}

static int do_acquire_user_credentials(int sock,
                                        const char *ticket,
                                        char* creds,
                                        size_t *creds_len)
{
    struct sockaddr_un remote;
    struct timeval timeout;
    int ret, len;
    fd_set rfds;

    memset(&remote, 0, sizeof(remote));
    remote.sun_family = AF_UNIX;
    strncpy(remote.sun_path, CREDENTIAL_CHANNEL, sizeof(remote.sun_path) - 1);
    len = SUN_LEN(&remote);
    remote.sun_path[0] = '\0';

    if (connect(sock, (struct sockaddr *)&remote, len) == -1) {
        D(("connect() failed."));
        return -1;
    }
    
    if (set_sock_non_blocking(sock) == -1) {
        return -1;
    }

    do  {
        ret = send(sock, ticket, strlen(ticket), 0);
    } while ((ret == -1) && (errno == EINTR));

    if (ret == -1) {
        D(("send() failed."));
        return -1;
    }
    
    do  {
        FD_ZERO(&rfds);
        FD_SET(sock, &rfds);
        timeout.tv_sec = 3;
        timeout.tv_usec = 0;
        ret = select(sock + 1, &rfds, NULL, NULL, &timeout);
    } while ((ret == -1) && (errno == EINTR));
    
    if (ret == -1) {
        D(("select() failed."));
        return -1;
    } else if (ret == 0) {
        D(("recv() timeout."));
        return -1;
    }
    
    if (FD_ISSET(sock, &rfds)) {
        do  {
            ret = recv(sock, creds, *creds_len, 0);
        } while ((ret == -1) && (errno == EINTR));
    }

    if (ret == -1) {
        D(("recv() failed."));
        return -1;
    }
    
    *creds_len = ret;

    return 0;
}

int acquire_user_credentials(const char *ticket,
                             char **username,
                             char **password)
{
    char creds[0x100];
    size_t creds_len = sizeof(creds);
    int sock;
    int ret;

    sock = socket(AF_UNIX,SOCK_STREAM, 0);
    if (sock == -1) {
        D(("socket() failed."));
        return -1;
    }
    
    ret = do_acquire_user_credentials(sock, ticket, creds, &creds_len);
    
    close(sock);
    
    if (ret == 0) {
        ret = parse_credentials_buffer(creds, creds_len, username, password);
        if (ret != 0) {
            D(("failed to parse credentials."));
        }
    } else {
        D((" %s (errno = %d)", strerror(errno), errno));
    }
    
    _pam_overwrite_n(creds, creds_len);

    return ret;
}
