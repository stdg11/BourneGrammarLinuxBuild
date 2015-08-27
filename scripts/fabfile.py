#!/usr/bin/env python
# Daniel Grammatica | dan@t0xic.me
# https://github.com/stdg11/BourneGrammarLinuxBuild
#
# Fabfile for Fabric (fabfile.org)
# (see SYSMAN.md#configuration-management)
#
# Usage:
# fab definitio_name 
# e.g. fab pubkey_distribute
 
from fabric.api import *
import cobbler.api as capi
import socket
import paramiko

env.colorize_errors = True # Colour Errors as Red, Warnings as Magenta

### Retrive list of systems from Cobbler insert them in env.hosts ###
handle = capi.BootAPI()
hostlist = []

for system in handle.systems():
  hostlist += [(system.name)]

env.hosts = hostlist

### Return uptime from hosts ###
@task
def uptime():
  if is_host_up(env.host, int(env.port)) is True:
    run('uptime')

### Function to check if host is up ###
def is_host_up(host, port):
    original_timeout = socket.getdefaulttimeout()
    new_timeout = 3
    socket.setdefaulttimeout(new_timeout)
    host_status = False
    try:
        transport = paramiko.Transport((host, port))
        host_status = True
    except:
        print('***Warning*** Host {host} on port {port} is down.'.format(
            host=host, port=port)
        )
    socket.setdefaulttimeout(original_timeout)
    return host_status

### push out serveradmin public key for passwordless login ###
@task
def pubkey_distribute():
	""""Create a pair of keys (if needed) and distribute the pubkey to hosts"""
	with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
		if local('ls ~/.ssh/id_rsa.pub').failed:
			local('ssh-keygen -N "" -q -f ~/.ssh/id_rsa -t rsa')
			local('ssh-add')
		run('mkdir .ssh')
		put('~/.ssh/id_rsa.pub','/home/serveradmin/.ssh/authorized_copy')
		run('cat /home/serveradmin/.ssh/authorized_copy >> /home/serveradmin/.ssh/authorized_keys')
		local('sudo chown $(whoami):$(whoami) /etc/ssh/ssh_config')
		local('echo "StrictHostKeyChecking no" >> /etc/ssh/ssh_config')
		local('sudo chown root:root /etc/ssh/ssh_config')

## Main function to setup workstations ###
@task
def ubuntu_setup():
  """Main setup for workstations"""
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      restore_repo()
      update()
      sudo("apt-get install realmd ntp git emacs libpam-mount cifs-utils")
      file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/default/grub","/etc/default/grub",use_sudo=True)
      sudo("update-grub")
      sudo("systemctl set-default multi-user.target")
      file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/ntp.conf","/etc/ntp.conf",use_sudo=True)
      sudo("service ntp restart")
      sudo("realm join --one-time-password bourne-grammar.lincs.sch.uk")

@task
def restore_repo():
  """ Restore default ubuntu repositories """
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      put("~/BourneGrammarLinuxBuild/configs/desktop/etc/apt/sources.list","/home/serveradmin/sources.list")
      sudo("mv /home/serveradmin/sources.list /etc/apt/sources.list",shell=False)

@task
@parallel
def update():
    """Update package list"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")

@task
@parallel
def install(package):
    """Install a package"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            for retry in range(2):
                if sudo("apt-get -y install %s" % package).failed:
                    local("echo INSTALLATION FAILED FOR %s: was installing %s $(date) >> ~/fail.log" % (env.host,package))
                else:
                    break

@task
@parallel
def install_auto(package):
    """Install a package answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s' % package)

@task
@parallel
def uninstall(package):
    """Uninstall a package"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get -y remove %s" % package)

@task
@parallel
def upgrade():
    """Upgrade packages"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo("apt-get -y upgrade")

@task 
@parallel
def upgrade_auto():
    """Update apt-get and Upgrade apt-get answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo('apt-get upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')

@task
def file_put(localpath, remotepath):
    """Put file from local path to remote path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            put(localpath,remotepath)

@task
def file_get(remotepath, localpath):
    """Get file from remote path to local path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            get(remotepath,localpath+'.'+env.host)

@task
def file_remove(remotepath):
    """Remove file at remote path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("rm -r %s" % remotepath)
