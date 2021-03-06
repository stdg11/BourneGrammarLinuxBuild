#!/usr/bin/env python
# Daniel Grammatica | dan@t0xic.me
# https://github.com/stdg11/BourneGrammarLinuxBuild
#
# Fabfile for Fabric (fabfile.org)
# (see SYSMAN.md#configuration-management)
#
# Usage:
# fab -H role definition_name 
# e.g. fab -H ICT1 pubkey_distribute
 
from fabric.api import *
import cobbler.api as capi
import socket
import paramiko

### Retrieve list of systems from Cobbler insert them in env.hosts ###                                    
handle = capi.BootAPI()
hostlist = []
env.roledefs = {
  'ICT1': [],
  'ICT2': [],
  'SC1': [],
  'SC2': [],
  'ALL' : []
}

for system in handle.systems():
  hostlist += [(system.name)]

env.roledefs["ALL"].append(hostlist)

for host in hostlist:
  if "LICT1" in host:
    env.roledefs['ICT1'].append(host)
  elif "LICT2" in host:
    env.roledefs['ICT2'].append(host)
  elif "LSC1" in host:
    env.roledefs['SC1'].append(host)
  elif "LSC2" in host:
    env.roledefs['SC2'].append(host)

### Variables ###                                                                               

env.colorize_errors = True # Colour Errors 
env.password = "" # Sudo Password               
ad_password = "" # Domain Admin Password  

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

### Function to install sublime-text3 ###

@task
@parallel
def install_sublime():
  """ Install sublime-text3 """
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      sudo("add-apt-repository -y ppa:webupd8team/sublime-text-3")
      sudo("apt-get update")
      sudo("apt-get install -y sublime-text-installer")

### push out serveradmin public key for passwordless login ###

@task
def pubkey_distribute():
	"""Create a pair of keys (if needed) and distribute the pubkey to hosts"""
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
@parallel
def ubuntu_setup():
  """Main setup for workstations"""
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      restore_repo()
      install_sublime()
      sudo("apt-get install -y emacs git xubuntu-desktop lynx idle idle3 python3 pandoc")
      update_grub()
      join_domain()
      mount_homedrive()
      dotfiles()
      startx_restore()
      sudoers()
      sssd_conf_push()
      sudo("reboot")

### Push sssd.conf to remote workstations ###

@task
@parallel
def sssd_conf_push():
  """Push sssd.conf to remote workstations"""
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/sssd/sssd.conf","/home/serveradmin/sssd.conf")
            sudo("mv /home/serveradmin/sssd.conf /etc/sssd/sssd.conf")
            sudo("chown root:root /etc/sssd/sssd.conf")
            sudo("chmod 0600 /etc/sssd/sssd.conf")
            sudo("service sssd restart")


### Return uptime from hosts ###                                                                                       

@task
@parallel
def uptime():
  if is_host_up(env.host, int(env.port)) is True:
    run('uptime')


### Add global alias for startxfce4 to startx

@task
@parallel
def startx_restore():
  """Add global alias for startxfce4 to startx"""
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/X11/Xsession","/home/serveradmin/Xsession")
      sudo("mv /home/serveradmin/Xsession /etc/X11/Xsession")

### Dotfiles persistant across machines ###

@task
@parallel
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
@parallel
def join_domain():
  """ Task to join Active Directory domain """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            splithost = env.host.split(".")
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
@parallel
def change_timezone():
  """ Task to change timezone to london """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:  
            sudo("echo 'Europe/London' | tee /etc/timezone")
            sudo("dpkg-reconfigure --frontend noninteractive tzdata")


### Mount users home drives ###

@task
@parallel
def mount_homedrive():
  """ Mount user home drives """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/security/pam_mount.conf.xml","/home/serveradmin/pam_mount.conf.xml")
            sudo("mv /home/serveradmin/pam_mount.conf.xml /etc/security/pam_mount.conf.xml")

### Add linuxadmin group to sudoers ###
            
@task
@parallel
def sudoers():
  """ Task to add linuxadmin group to sudoers """
  with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/scripts/sudoers.sh", "/home/serveradmin/sudoers.sh")
            sudo("chmod +x /home/serveradmin/sudoers.sh")
            sudo("./home/serveradmin/sudoers.sh")
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/sudoers.d/domainusers", "/home/serveradmin/domainusers")
            sudo("mv /home/serveradmin/domainusers /etc/sudoers.d/domainusers")
            sudo("chown root:root /etc/sudoers.d/domainusers")
            sudo("chmod 440 /etc/sudoers.d/domainusers")

### Update grub so Windows boots first ###

@task
@parallel
def update_grub():
 """ Task to update grub """
 with settings(linewise=True,warn_only=True):
          if is_host_up(env.host, int(env.port)) is True:
            file_put("~/BourneGrammarLinuxBuild/configs/desktop/etc/default/grub","/home/serveradmin/grub")
            sudo("mv /home/serveradmin/grub /etc/default/grub")
            sudo("update-grub")

### Restore default Ubuntu repositories ###

@task
@parallel
def restore_repo():
  """ Restore default ubuntu repositories """
  with settings(linewise=True,warn_only=True):
    if is_host_up(env.host, int(env.port)) is True:
      put("~/BourneGrammarLinuxBuild/configs/desktop/etc/apt/sources.list","/home/serveradmin/sources.list")
      sudo("mv /home/serveradmin/sources.list /etc/apt/sources.list")

### apt-get update ###

@task
@parallel
def update():
    """Update package list"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            sudo("apt-get update")

### Install a package ###

@task
@parallel
def install(package):
    """Install a package"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
          for retry in range(2):
                if sudo("apt-get -y install %s" % package).failed:
                    local("echo INSTALLATION FAILED FOR %s: was installing %s $(date) >> ~/fail.log" % (env.host,package))
                else:
                    break

### Install a package answering yes to all questions ###

@task
@parallel
def install_auto(package):
    """Install a package answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
          sudo('DEBIAN_FRONTEND=noninteractive /usr/bin/apt-get install -o Dpkg::Options::="--force-confold" --force-yes -y %s' % package)

### Uninstall a package ###

@task
@parallel
def uninstall(package):
    """Uninstall a package"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
            sudo("apt-get -y remove %s" % package)

### Upgrade packages ###

@task
@parallel
def upgrade():
    """Upgrade packages"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
          sudo("apt-get -y upgrade")

### Upgrade answering yes to all questions  ###

@task
@parallel
def upgrade_auto():
    """Upgrade answering yes to all questions"""
    with settings(linewise=True, warn_only=True):
        if is_host_up(env.host, int(env.port)) is True:
          sudo('DEBIAN_FRONTEND=noninteractive apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" upgrade"')

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
