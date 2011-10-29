
#include <stdlib.h>

extern int acquire_user_credentials(const char *token,
                                     char **username,
                                     char **password);

int main(int argc,char **argv)
{
    char *token = "token";
    char *username = NULL;
    char *password = NULL;

    if (argc > 1) {
	token = argv[1];
    }
    
    if (acquire_user_credentials(token, &username, &password) == 0) {
        free(username);
        free(password);
    }
    
    return 0;
}
