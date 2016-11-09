#!/usr/bin/python3.5
#-*- coding:utf-8 -*-

from subprocess import call
import os
import functools
import pexpect

username = r'abc'
password = r'123'
userauthorizedkeys = r'%s.pub'% username
call_shell = functools.partial(call, shell=True, stdin=None, stdout=None, stderr=None)

def dir_exists(dirpath):
    if os.path.exists(r'%s' % dirpath):
        return 'dir is exists'
    else:
        os.makedirs(r'%s' % dirpath)
        return 'mkdir successful'

def adduser(username,password):
    try:
        call_shell(r'chattr -i /etc/passwd /etc/group /etc/shadow /etc/sudoers /etc/profile')
        map(dir_exists, [r'/data/home', r'/data/backup/authorized_keys_bak'])
        call_shell(r'useradd %s' % username)
        call_shell(r'echo %s | passwd --stdin %s' % (password, username))
        try:
            ssh = pexpect.spawn('/usr/bin/su %s -c ssh-keygen' % username, timeout=5)
            ssh.expect(r'which to save the key')
            ssh.sendline('\r')
            ssh.expect(r'empty for no passphrase')
            ssh.sendline('\r')
            ssh.expect(r'Enter same passphrase again:')
            ssh.sendline('\r')
            sshlogfile = open('/root/ssh.log', 'wb')
            ssh.logfile = sshlogfile
            ssh.expect(pexpect.EOF)
        except Exception as e:
            print(e)
            pass
    except Exception as addusererror:
        print(addusererror)
    else:
        print('adduser successful !')
    with open(r'/data/home/%s/.bash_profile' % username, 'a') as f:
        f.write('\nif [ "$PS1" ];then\n  . /usr/local/pateo/slogin.sh\nfi')
    try:
        if os.path.exists(r'/data/backup/authorized_keys_bak/%s' % userauthorizedkeys):
            call_shell(r'mv /data/backup/authorized_keys_bak/%s /data/backup/authorized_keys_bak/%s.bak' % (userauthorizedkeys, userauthorizedkeys))
        call_shell(r'mv /data/home/%s/.ssh/id_rsa.pub /data/home/%s/.ssh/%s' % (username, username, userauthorizedkeys))
        call_shell(r'cp /data/home/%s/.ssh/%s /data/backup/authorized_keys_bak/' % (username, userauthorizedkeys))
        call_shell(r'chattr +i /etc/passwd /etc/group /etc/shadow /etc/sudoers /etc/profile')
    except Exception as backupkeyerror:
        print(backupkeyerror)
    else:
        print('backupkey successful !')

if __name__ == '__main__':
    try:
        adduser(username, password)
    except Exception as e:
        print(e)