#!/usr/bin/env python
from fabric.api import *
import cobbler.api as capi

handle = capi.BootAPI()
hostlist = []

for system in handle.systems():
  hostlist = [(system.name)]

env.hosts = hostlist

def print_systems():
  print(env.hosts)

def uptime():
  run('uptime')

def pubkey_distribute():
	""""Create a pair of keys (if needed) and distribute the pubkey to hosts"""
	with settings(linewise=True,warn_only=True):
		if local('ls ~/.ssh/id_rsa.pub').failed:
			local('ssh-keygen -N "" -q -f ~/.ssh/id_rsa -t rsa')
			local('ssh-add')
		run('mkdir .ssh')
		put('~/.ssh/id_rsa.pub','/home/serveradmin/.ssh/authorized_copy')
		run('cat /home/serveradmin/.ssh/authorized_copy >> /home/serveradmin/.ssh/authorized_keys')
		local('sudo chown $(whoami):$(whoami) /etc/ssh/ssh_config')
		local('echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config')
		local('sudo chown root:root /etc/ssh/ssh_config')
