#!/usr/bin/python

import getpass, socket, struct

def pack(user, password, domain = ''):
    if domain != '':
        username = user + '@' + domain
    else:
        username = user
    username = username.encode('utf-8')
    password = password.encode('utf-8')
    s = struct.pack('>I%ds%ds' % (len(username), len(password) + 1),
                    len(username), username, password)
    return s

def main():
    user = raw_input('user: ')
    password = getpass.getpass('password: ')
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect('/tmp/gdm-rhevcred-plugin')
    sock.send(pack(user, password))

if __name__ == "__main__":
    main()
