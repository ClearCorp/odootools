#!/usr/bin/python2

import os
import platform

def check_root():
    uid = os.getuid()
    return uid == 0

def get_os():
    platform_system = platform.system()
    if os_name == "Linux":
        return platform.linux_distribution()
    elif os_name == "Mac":
        return platform.mac_ver()
    elif os_name == "Windows":
        return platform.win32_ver()
    return False

def regenerate_ssh_keys():
    regen_script = open('/etc/regen-ssh-keys.sh', 'w')
    regen_script.write('''
#!/bin/bash
rm -f /etc/ssh/ssh_host_*
ssh-keygen -f /etc/ssh/ssh_host_rsa_key -t rsa -N ''
ssh-keygen -f /etc/ssh/ssh_host_dsa_key -t dsa -N ''

sed '/regen-ssh-keys.sh/d' /etc/rc.local > /etc/rc.local.tmp
cat /etc/rc.local.tmp > /etc/rc.local
rm -f /etc/rc.local.tmp

rm -f \$0
''')
    regen_script.close()
    os.chmod('/etc/regen-ssh-keys.sh', 0755)
    
    rc_local = open('/etc/rc.local', 'a')
    rc_local.write('/etc/regen-ssh-keys.sh\n')
    rc_local.close()

