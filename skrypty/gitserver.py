#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import logging
import subprocess
import ldap

logging.basicConfig(filename='/log',level=logging.DEBUG)

LDAP_ADDRESS = 'ldap://localhost/'
LDAP_SUFFIX = "dc=icis,dc=pcz,dc=pl"
BIND_ACCOUNT = 'cn=admin,' + LDAP_SUFFIX
BIND_PASSWORD = 'test'



def check_permissions(owner_name, guest_name, repo):
    """
    Check for permissions for 'guest_name' to repository 'repo' which belongs to 'owner_name'
    0 - no permissions
    1 - RO
    2 - RW
    """
    
    f = open('/log', 'a')
    l = ldap.initialize(LDAP_ADDRESS, trace_level=2, trace_file=f)
    l.simple_bind(BIND_ACCOUNT, BIND_PASSWORD)
    f.write(repo + '\n')
    repo = repo.split('/')[-1]
    f.write(repo + '\n')


    path = "repo=%s,ou=git,uid=%s,ou=users," % (repo, owner_name) + LDAP_SUFFIX
    f.write("asasa")
    f.write(path)
    result = l.search_s(path,ldap.SCOPE_BASE, '(objectClass=repository)', ('userRO', 'userRW',))


    if 'userRO' in result[0][1]:
        if guest_name in result[0][1]['userRO']:
            return 1
    elif 'userRW' in result[0][1]:
        if guest_name in result[0][1]['userRW']:
            return 2
    else:
        return 0

if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        exit()
        
    try:
        ssh_command = os.environ['SSH_ORIGINAL_COMMAND']
        owner_name = os.environ['USER']
    except:

        exit()
        
    try:
        command, repository = ssh_command.split()
    except:
        exit()

    try:
        guest_name = sys.argv[1]
    except:
        exit()

    repository = repository[1:-1]

    valid_commands = ('git-receive-pack', 'git-upload-pack',)
    f = open('/log', 'a')
    f.write(ssh_command)
    
    if command not in valid_commands:
        exit()
    
    permission = check_permissions(owner_name, guest_name, repository)
      
    if not permission:
        sys.stderr.write("Użytkownik %s nie ma dostępu do tego repozytorium.\n" % (guest_name,))
        exit()
    
    if permission == 1:
        if command == 'git-upload-pack':
            pass
        elif command == 'git-receive-pack':
            sys.stderr.write("Użytkownik %s nie ma możliwości zapisu do tego repozytorium.\n" % (guest_name,))
            exit()
    elif not (permission == 2 and (command == 'git-upload-pack' or command == 'git-receive-pack')):
        sys.stderr.write("Użytkownik %s nie ma dostępu do tego repozytorium22.\n" % (guest_name,))
        exit()
    
    subprocess.call(["git", "shell", "-c", ssh_command])
