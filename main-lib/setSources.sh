#!/bin/bash

#~ Adds key to apt
function addKey {
	if [[ `gpg --list-keys | grep -c $1` == 0 ]]; then
		gpg --recv-keys $1
		gpg --armor --export $1 | apt-key add -
	fi
}

function setSources_ubuntu {
	archive="archive"
	if [[ `grep .ec2 /etc/apt/sources.list -c` > 0 ]]; then
		archive=`egrep [^./]*\.ec2 /etc/apt/sources.list -o -m 1`
	fi
# Ubuntu repository
	cat > /etc/apt/sources.list << EOF
# See http://help.ubuntu.com/community/UpgradeNotes for how to upgrade to
# newer versions of the distribution.

## N.B. software from universe repository is ENTIRELY UNSUPPORTED by the Ubuntu
## team. Also, please note that software in universe WILL NOT receive any
## review or updates from the Ubuntu security team.

## N.B. software from multiverse repository is ENTIRELY UNSUPPORTED by the Ubuntu 
## team, and may not be under a free licence. Please satisfy yourself as to 
## your rights to use the software. Also, please note that software in 
## multiverse WILL NOT receive any review or updates from the Ubuntu
## security team.

## N.B. software from updates repository are major bug fix updates produced after the final release of the
## distribution.

## N.B. software from backports repository may not have been tested as
## extensively as that contained in the main release, although it includes
## newer versions of some applications which may provide useful features.
## Also, please note that software in backports WILL NOT receive any review
## or updates from the Ubuntu security team.

## N.B. software from partner repository is not part of Ubuntu, but is offered by Canonical and the
## respective vendors as a service to Ubuntu users.

# Main repository
deb http://$archive.ubuntu.com/ubuntu/ $1 main
deb http://$archive.ubuntu.com/ubuntu/ $1-updates main
deb http://$archive.ubuntu.com/ubuntu/ $1-security main
#deb http://$archive.ubuntu.com/ubuntu/ $1-backports main
#deb-src http://$archive.ubuntu.com/ubuntu/ $1 main
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-updates main
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-security main
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-backports main

# Restricted repository
deb http://$archive.ubuntu.com/ubuntu/ $1 restricted
deb http://$archive.ubuntu.com/ubuntu/ $1-updates restricted
deb http://$archive.ubuntu.com/ubuntu/ $1-security restricted
#deb http://$archive.ubuntu.com/ubuntu/ $1-backports restricted
#deb-src http://$archive.ubuntu.com/ubuntu/ $1 restricted
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-updates restricted
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-security restricted
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-backports restricted

# Universe repository
deb http://$archive.ubuntu.com/ubuntu/ $1 universe
deb http://$archive.ubuntu.com/ubuntu/ $1-updates universe
deb http://$archive.ubuntu.com/ubuntu/ $1-security universe
#deb http://$archive.ubuntu.com/ubuntu/ $1-backports universe
#deb-src http://$archive.ubuntu.com/ubuntu/ $1 universe
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-updates universe
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-security universe
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-backports universe

# Multiverse repository
deb http://$archive.ubuntu.com/ubuntu/ $1 multiverse
deb http://$archive.ubuntu.com/ubuntu/ $1-updates multiverse
deb http://$archive.ubuntu.com/ubuntu/ $1-security multiverse
#deb http://$archive.ubuntu.com/ubuntu/ $1-backports multiverse
#deb-src http://$archive.ubuntu.com/ubuntu/ $1 multiverse
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-updates multiverse
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-security multiverse
#deb-src http://$archive.ubuntu.com/ubuntu/ $1-backports multiverse

# Partner repository
deb http://$archive.canonical.com/ubuntu $1 partner
#deb-src http://$archive.canonical.com/ubuntu $1 partner
EOF
}

function setSources_webmin {
	# Webmin repository
	cat > /etc/apt/sources.list.d/webmin.list << EOF
# Webmin repository
deb http://download.webmin.com/download/repository sarge contrib
EOF
	wget -q http://www.webmin.com/jcameron-key.asc -O - | apt-key add -
}

function setSources_bazaar {
	apt-get -qq update
	apt-get -yqq install python-software-properties
	
	add-apt-repository ppa:bzr/ppa
	add-apt-repository ppa:bzr-explorer-dev/ppa
}

function setSources {
	#Adds add-apt-repository
	setSources_ubuntu $1
	setSources_webmin $1
	setSources_bazaar $1
}
