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
		archive=`egrep [^./]*\.ec2 /etc/apt/sources.list -o -m 1`".archive"
	fi
# Ubuntu repository
	cat > /etc/apt/sources.list << EOF
# main repository
deb mirror://mirrors.ubuntu.com/mirrors.txt $1 main
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-updates main
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-security main
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-backports main
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed main
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1 main
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-updates main
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-security main
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-backports main
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed main

# restricted repository
deb mirror://mirrors.ubuntu.com/mirrors.txt $1 restricted
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-updates restricted
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-security restricted
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-backports restricted
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed restricted
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1 restricted
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-updates restricted
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-security restricted
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-backports restricted
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed restricted

# universe repository
deb mirror://mirrors.ubuntu.com/mirrors.txt $1 universe
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-updates universe
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-security universe
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-backports universe
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed universe
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1 universe
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-updates universe
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-security universe
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-backports universe
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed universe

# multiverse repository
deb mirror://mirrors.ubuntu.com/mirrors.txt $1 multiverse
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-updates multiverse
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-security multiverse
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-backports multiverse
deb mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed multiverse
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1 multiverse
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-updates multiverse
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-security multiverse
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-backports multiverse
deb-src mirror://mirrors.ubuntu.com/mirrors.txt $1-proposed multiverse

# Partner repository
deb http://archive.canonical.com/ubuntu $1 partner
deb-src http://archive.canonical.com/ubuntu $1 partner
EOF
}

function setSources_zentyal {
	if [[ $1 == "lucid" ]]; then
		# Zentyal repository
		cat > /etc/apt/sources.list.d/zentyal.list << EOF
	# zentyal repository
	deb http://ppa.launchpad.net/zentyal/2.0/ubuntu lucid main
EOF
		apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 10E239FF
	fi
}

function setSources_webmin {
	# Webmin repository
	cat > /etc/apt/sources.list.d/webmin.list << EOF
# Webmin repository
deb http://download.webmin.com/download/repository sarge contrib
EOF
	wget -q http://www.webmin.com/jcameron-key.asc -O - | apt-key add -
}

function setSources {
	#Adds add-apt-repository
	setSources_ubuntu $1
	setSources_zentyal $1
	setSources_webmin $1
}

function setSources_disable_src {
	# Comments all deb-src lines
	sed -i "s/^\(\s*deb-src.*$\)/# &/g" /etc/apt/sources.list
}

function setSources_disable_restricted {
	# Comments all restricted repo lines
	sed -i "s/^\(\s*deb.*restricted.*$\)/# &/g" /etc/apt/sources.list
}

function setSources_disable_universe {
	# Comments all universe repo lines
	sed -i "s/^\(\s*deb.*universe.*$\)/# &/g" /etc/apt/sources.list
}

function setSources_disable_multiuniverse {
	# Comments all multiuniverse repo lines
	sed -i "s/^\(\s*deb.*multiuniverse.*$\)/# &/g" /etc/apt/sources.list
}

function setSources_disable_proposed {
	# Comments all proposed repo lines
	sed -i "s/^\(\s*deb.*-proposed.*$\)/# &/g" /etc/apt/sources.list
}

function setSources_disable_backports {
	# Comments all backports repo lines
	sed -i "s/^\(\s*deb.*-backports.*$\)/# &/g" /etc/apt/sources.list
}