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
deb http://archive.ubuntu.com/ubuntu/ $dist main
deb http://archive.ubuntu.com/ubuntu/ $dist-updates main
deb http://archive.ubuntu.com/ubuntu/ $dist-security main
#deb http://archive.ubuntu.com/ubuntu/ $dist-backports main
#deb-src http://archive.ubuntu.com/ubuntu/ $dist main
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-updates main
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-security main
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-backports main

# Restricted repository
deb http://archive.ubuntu.com/ubuntu/ $dist restricted
deb http://archive.ubuntu.com/ubuntu/ $dist-updates restricted
deb http://archive.ubuntu.com/ubuntu/ $dist-security restricted
#deb http://archive.ubuntu.com/ubuntu/ $dist-backports restricted
#deb-src http://archive.ubuntu.com/ubuntu/ $dist restricted
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-updates restricted
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-security restricted
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-backports restricted

# Universe repository
deb http://archive.ubuntu.com/ubuntu/ $dist universe
deb http://archive.ubuntu.com/ubuntu/ $dist-updates universe
deb http://archive.ubuntu.com/ubuntu/ $dist-security universe
#deb http://archive.ubuntu.com/ubuntu/ $dist-backports universe
#deb-src http://archive.ubuntu.com/ubuntu/ $dist universe
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-updates universe
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-security universe
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-backports universe

# Multiverse repository
deb http://archive.ubuntu.com/ubuntu/ $dist multiverse
deb http://archive.ubuntu.com/ubuntu/ $dist-updates multiverse
deb http://archive.ubuntu.com/ubuntu/ $dist-security multiverse
#deb http://archive.ubuntu.com/ubuntu/ $dist-backports multiverse
#deb-src http://archive.ubuntu.com/ubuntu/ $dist multiverse
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-updates multiverse
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-security multiverse
#deb-src http://archive.ubuntu.com/ubuntu/ $dist-backports multiverse

# Partner repository
deb http://archive.canonical.com/ubuntu $dist partner
#deb-src http://archive.canonical.com/ubuntu $dist partner
EOF

# Webmin repository

cat > /etc/apt/sources.list.d/webmin.list << EOF
# Webmin repository
deb http://download.webmin.com/download/repository sarge contrib
EOF

wget -q http://www.webmin.com/jcameron-key.asc -O - | apt-key add -
