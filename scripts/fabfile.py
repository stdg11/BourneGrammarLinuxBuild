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

### Retrive list of systems from Cobbler insert them in env.hosts ###
handle = capi.BootAPI()
hostlist = []

for system in handle.systems():
  hostlist += [(system.name)]

### Variables ###

env.colorize_errors = True # Colour Errors as Red, Warnings as Magenta 
env.hosts = hostlist
env.password = "" # Sudo password
ad_password = "" # Password to join domain


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

### Main function to setup workstations ###

@task
def ubuntu_setup():
  """Main setup for workstations"""
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      restore_repo()
      install("emacs")
      install("git")
      install("xubuntu-desktop")
      install("lynx")
      install("idle")
      update_grub()
      join_domain()
      mount_homedrive()
      dotfiles()
      startx_restore()
      sudoers()
      sudo("reboot")

### Add global alias for startxfce4 to startx

@task
def startx_restore():
  """Add global alias for startxfce4 to startx"""
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/X11/Xsession","/home/serveradmin/Xsession")
      sudo("mv /home/serveradmin/Xsession /etc/X11/Xsession")

### Dotfiles persistant across machines ###

@task
def dotfiles():
  """ Task to make dotfiles persestant across machines """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/usr/bin/dotfiles","/home/serveradmin/dotfiles")
            sudo("mv /home/serveradmin/dotfiles /usr/bin/dotfiles")
            sudo("chmod +x /usr/bin/dotfiles")
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/xdg/autostart/dotfiles.desktop","/home/serveradmin/dotfiles.desktop")
            sudo("mv /home/serveradmin/dotfiles.desktop /etc/xdg/autostart/dotfiles.desktop")

### Join an Active Directory Domain ###

@task
def join_domain():
  """ Task to join Active Directory domain """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            splithost = env.host.split(".")
            update()
            sudo("apt-get install -y realmd ntp sssd sssd-tools samba-common krb5-user packagekit samba-common-bin samba-libs cifs-utils libpam-mount adcli ntp")
            sudo("echo 'Europe/London' | tee /etc/timezone")
            sudo("dpkg-reconfigure --frontend noninteractive tzdata")
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/ntp.conf","/home/serveradmin/ntp.conf")
            sudo("mv /home/serveradmin/ntp.conf /etc/ntp.conf")
            sudo("service ntp restart")
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/realmd.conf","/home/serveradmin/realmd.conf")
            sudo("mv /home/serveradmin/realmd.conf /etc/realmd.conf")
            sudo("chown root:root /etc/realmd.conf")
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/krb5.conf","/home/serveradmin/krb5.conf")
            sudo("mv /home/serveradmin/krb5.conf /etc/krb5.conf")
            sudo("chown root:root /etc/krb5.conf")
            sudo("echo %s | kinit Admin@BOURNE-GRAMMAR.LINCS.SCH.UK" % ad_password )
            sudo("realm join bourne-grammar.lincs.sch.uk --user-principal=%s/Admin@BOURNE-GRAMMAR.LINCS.SCH.UK --unattended" % splithost[0] )
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/sssd/sssd.conf","/home/serveradmin/sssd.conf")
            sudo("mv /home/serveradmin/sssd.conf /etc/sssd/sssd.conf")
            sudo("chown root:root /etc/sssd/sssd.conf")
            sudo("chmod 0600 /etc/sssd/sssd.conf")
            sudo("service sssd restart")
          
### Change keyboard layout ###

@task
def change_keyboard():
  """ Task to change keyboard layout """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:  
            sudo("echo 'Europe/London' | tee /etc/timezone")
            sudo("dpkg-reconfigure --frontend noninteractive tzdata")


### Mount users home drives ###

@task
def mount_homedrive():
  """ Mount user home drives """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/security/pam_mount.conf.xml","/home/serveradmin/pam_mount.conf.xml")
            sudo("mv /home/serveradmin/pam_mount.conf.xml /etc/security/pam_mount.conf.xml")

### Add linuxadmin group to sudoers ###
            
@task
def sudoers():
  """ Task to add linuxadmin group to sudoers """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/scripts/sudoers.sh", "/home/serveradmin/sudoers.sh")
            sudo("chmod +x /home/serveradmin/sudoers.sh")
            sudo("./home/serveradmin/sudoers.sh")
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/sudoers.d/domainusers", "/home/serveradmin/domainusers")
            sudo("mv /home/serveradmin/domainusers /etc/sudoers.d/domainusers")
            sudo("chmod 0440 /etc/sudoers.d/domainusers")

### Update grub so Windows boots first ###

@task
def update_grub():
 """ Task to update grub """
 with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/default/grub","/home/serveradmin/grub")
            sudo("mv /home/serveradmin/grub /etc/default/grub")
            sudo("update-grub")

### Restore default Ubuntu repositories ###

@task
def restore_repo():
  """ Restore default ubuntu repositories """
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      put("~/BourneGrammarLinuxBuild/configs/desktop/etc/apt/sources.list","/home/serveradmin/sources.list")
      sudo("mv /home/serveradmin/sources.list /etc/apt/sources.list")

### apt-get update ###

@task
def update():
    """Update package list"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            sudo("apt-get update")

### apt-get install ###

@task
def install(package):
    """Install a package"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            sudo("apt-get update")
            for retry in range(2):
                if sudo("apt-get -y install %s" % package).failed:
                    local("echo INSTALLATION FAILED FOR %s: was installing %s $(date) >> ~/fail.log" % (env.host,package))
                else:
                    break

### ###

@task
def install_auto(package):
    """Install a package answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            sudo("apt-get update")
            sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s' % package)

### ###

@task
def uninstall(package):
    """Uninstall a package"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get -y remove %s" % package)

### ###

@task
def upgrade():
    """Upgrade packages"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo("apt-get -y upgrade")

### ###

@task 
def upgrade_auto():
    """Update apt-get and Upgrade apt-get answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host):
            sudo("apt-get update")
            sudo('apt-get upgrade -o Dpkg::Options::="--force-confold" --force-yes -y')

### Copy a file from local to remote ###

@task
def file_put(localpath, remotepath):
    """Put file from local path to remote path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            put(localpath,remotepath)

### Download file from remote to local ###

@task
def file_get(remotepath, localpath):
    """Get file from remote path to local path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            get(remotepath,localpath+'.'+env.host)

### Remove remote file

@task
def file_remove(remotepath):
    """Remove file at remote path"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            sudo("rm -r %s" % remotepath)
