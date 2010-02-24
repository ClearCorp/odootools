#!/bin/bash

function regenSSHKeys(){
		cat << EOF > /etc/rc2.d/S15ssh_gen_host_keys
#!/bin/bash
rm -f /etc/ssh/ssh_host_*
ssh-keygen -f /etc/ssh/ssh_host_rsa_key -t rsa -N ''
ssh-keygen -f /etc/ssh/ssh_host_dsa_key -t dsa -N ''
rm -f \$0
EOF
	chmod a+x /etc/rc2.d/S15ssh_gen_host_keys
}
