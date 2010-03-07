#!/bin/bash


if [[ `cat /etc/bash.bashrc | grep -c /etc/bash.bashrc-ccorp` == 0 ]]; then
	echo ". /etc/bash.bashrc-ccorp" >> /etc/bash.bashrc
	cp bash.bashrc-ccorp /etc/bash.bashrc-ccorp
fi