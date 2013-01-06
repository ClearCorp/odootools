#!/bin/bash

# Gets the name of any Ubuntu or Debian dist.
function getDist {
	if [[ `cat /etc/issue | grep -c Ubuntu` == 1 ]]; then
		if [[ `cat /etc/issue | grep -c 4.10` == 1 ]]; then
			eval "$1=warty"
		elif [[ `cat /etc/issue | grep -c 5.04` == 1 ]]; then
			eval "$1=hoary"
		elif [[ `cat /etc/issue | grep -c 5.10` == 1 ]]; then
			eval "$1=breezy"
		elif [[ `cat /etc/issue | grep -c 6.04` == 1 ]]; then
			eval "$1=dapper"
		elif [[ `cat /etc/issue | grep -c 6.10` == 1 ]]; then
			eval "$1=edgy"
		elif [[ `cat /etc/issue | grep -c 7.04` == 1 ]]; then
			eval "$1=feisty"
		elif [[ `cat /etc/issue | grep -c 7.10` == 1 ]]; then
			eval "$1=gutsy"
		elif [[ `cat /etc/issue | grep -c 8.04` == 1 ]]; then
			eval "$1=hardy"
		elif [[ `cat /etc/issue | grep -c 8.10` == 1 ]]; then
			eval "$1=intrepid"
		elif [[ `cat /etc/issue | grep -c 9.04` == 1 ]]; then
			eval "$1=jaunty"
		elif [[ `cat /etc/issue | grep -c 9.10` == 1 ]]; then
			eval "$1=karmic"
		elif [[ `cat /etc/issue | grep -c 10.04` == 1 ]]; then
			eval "$1=lucid"
		elif [[ `cat /etc/issue | grep -c 10.10` == 1 ]]; then
			eval "$1=maverick"
		elif [[ `cat /etc/issue | grep -c 11.04` == 1 ]]; then
			eval "$1=natty"
        elif [[ `cat /etc/issue | grep -c 11.10` == 1 ]]; then
            eval "$1=oneiric"
        elif [[ `cat /etc/issue | grep -c 12.04` == 1 ]]; then
            eval "$1=precise"
		# This has to be updated as soon as lucid succesor is announced.
		else
			eval "$1=error"
			return 1
		fi
	elif [[ `cat /etc/issue | grep -c Debian` == 1 ]]; then
		if [[ `cat /etc/issue | grep -c 2.0` == 1 ]]; then
			eval "$1=hamm"
		elif [[ `cat /etc/issue | grep -c 2.1` == 1 ]]; then
			eval "$1=slink"
		elif [[ `cat /etc/issue | grep -c 2.2` == 1 ]]; then
			eval "$1=potato"
		elif [[ `cat /etc/issue | grep -c 3.0` == 1 ]]; then
			eval "$1=woody"
		elif [[ `cat /etc/issue | grep -c 3.1` == 1 ]]; then
			eval "$1=sarge"
		elif [[ `cat /etc/issue | grep -c 4.0` == 1 ]]; then
			eval "$1=etch"
		elif [[ `cat /etc/issue | grep -c 5.0` == 1 ]]; then
			eval "$1=lenny"
		elif [[ `cat /etc/issue | grep -c 6.0` == 1 ]]; then
			eval "$1=squeeze"
		# This has to be updated as soon as squeeze succesor is announced.

		else
			eval "$1=error"
			return 1
		fi
	else
		eval "$1=error"
		return 1
	fi
	return 0
}
