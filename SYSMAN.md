<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
Change password to servradmin!!!

**Contents**

  - [Prerequisites](#prerequisites)
  - [Installing Cobbler](#installing-cobbler)
  - [Setup cobbler-web](#setup-cobbler-web)
  - [Adding Ubuntu Server image to Cobbler](#adding-ubuntu-server-image-to-cobbler)
  - [Configuring Preseed](#configuring-preseed)
  - [Dual Boot](#dual-boot)
  - [Importing systems from MS DHCP to Cobbler](#importing-systems-from-ms-dhcp-to-cobbler)
  - [Configuration management](#configuration-management)
- [setup fabric](#setup-fabric)
- [generate pair of keys [if absent], put public key to workstations](#generate-pair-of-keys-if-absent-put-public-key-to-workstations)
- [run fabrics init and main tasks](#run-fabrics-init-and-main-tasks)
  - [References](#references)
  - [TODO](#todo)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Prerequisites

Start with an install of Ubuntu/Debian Server with OpenSSH Server and networking setup/resolving correctly.

## Installing Cobbler

Head over to http://download.opensuse.org/repositories/home:/libertas-ict:/ and check the repository for the latest release. I will be using 2.6.9.

Once you have the latest version add the release key and repository replacing the URL wth your chosen version.
```bash
wget -q0 - http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/Release.key | sudo apt-key add -
sudo add-apt-repository "deb http://download.opensuse.org/repositories/home:/libertas-ict:/cobbler26/xUbuntu_14.04/ ./"
```

Update and Install cobbler and its dependencies.
```bash
sudo apt-get update
sudo apt-get install cobbler="2.6.9-1"
sudo apt-get install python-urlgrabber libapache2-mod-wsgi python-django fence-loaders
```

Edit tho Cobbler config file `/etc/cobbler/settings`

```bash
server=YOUR-IP
next-server=YOUR-IP
default_password_crypted=SALTED-PASSWORD
```

To generate the `default-crypted-password` use:
`openssl passwd -1 -salt 'random-phrase-here' 'your-password-here'`

Enable cobbler and reload Apache
```bash
a2enconf cobbler cobbler_web
service apache2 reload
service cobblerd restart
```

Obtain boot loaders
`sudo cobbler get-loaders`

Check the Cobbler configuration
`sudo cobbler check`

Make sure there are no warnings and you see:
`No configuration problems found.  All systems go.`

Once there are no errors run:
`sudo cobbler sync`

## Setup cobbler-web

Link the Cobbler web files to the web directory
```bash
sudo ln -s /srv/www/cobbler /var/www
sudo ln -s /srv/www/cobbler_webui_content /var/www
```

Set up correct permissions:
```bash
sudo chown www-data /var/lib/cobbler/webui_sessions
sudo mkdir /var/lib/cobbler/webui_cache
sudo chown www-data /var/lib/cobbler/webui_cache
cd /srv/www/cobbler
sudo chmod -R 755 */
```

Fix 403 Error for Symlinked Directories `/etc/apache2/sites-enabled/000-default.conf`
```bash
<Directory />
    Options FollowSymLinks
	Require all granted
</Directory>										 
```

Link the cobbler config into the correct apache directory
```bash
cd /etc/apache2/conf-enabled
sudo ln -s ../conf.d/cobbler_web.conf .
sudo ln -s ../conf.d/cobbler.conf .
```

Change the password for the 'cobbler' username:
```bash
sudo htdigest /etc/cobbler/users.digest "Cobbler" cobbler
```

Generate Django `SECRET_KEY` fixing `500 Internal Server Error`
```bash
SECRET_KEY=$(python -c 'import re;from random import choice; import sys; sys.stdout.write(re.escape("".join([choice("abcdefghijklmnopqrstuvwxyz0123456789^&*(-_=+)") for i in range(100)])))')
sudo sed --in-place "s/^SECRET_KEY = .*/SECRET_KEY = '${SECRET_KEY}'/" /usr/share/cobbler/web/settings.py
```

You should now be able to access Cobbler at http://SERVER-IP/cobbler_web

## Adding Ubuntu Server image to Cobbler

Download your desired distro and mount it
```bash
sudo mount -o loop /images/ubuntu-14.04.2-server-amd64.iso /mnt
```

Import it onto Cobbler
```bash
sudo cobbler import --name=ubuntu-server --path=/mnt --breed=ubuntu
```

If no errors were reported during the import, you can view details about the distros and profiles that were created during the import.
```bash
sudo cobbler distro list
sudo cobbler profile list
```

## Configuring Preseed

Copy the sample.seed file
```bash
sudo cp /var/lib/cobbler/kickstarts/sample.seed /var/lib/cobbler/kickstarts/ubuntu.seed
```

Assign the ubuntu.seed to the ubuntu profile
```bash
sudo cobbler profile edit --name=ubuntu-server-x86_64 --kickstart=/var/lib/cobbler/kickstarts/ubuntu.seed
```

## Dual Boot

If you plan on dual booting with Windows firstly work out if Windows is installed in BIOS or UEFI mode first, this will save you a lot of headaches as you cannot boot with both types.

Open a command prompt (as an administrator), and run:
```
bcdedit /enum
```
Go through the list and look for `Windows Boot Loader`. If your system is booted in EFI mode, the path value will be `\Windows\system32\winload.efi` (note the .efi extension - this will revert to .exe otherwise).

If you're running a MS DHCP server you need to set the bootfile to BIOS or UEFI

BIOS - `pxelinux.0`
UEFI (64-bit) - `grub/grub-x86_64.efi`

Alternatively if you're using a Linux DHCP server see:  
https://github.com/cobbler/cobbler/commit/7df50e72868b0981accd2e2bc3f7e56ab076

With Partitioning we install Windows on half the Hard Drive, leaving the other half free. Then install Ubuntu using free space:

```bash
d-i partman-auto/init_automatically_partition select biggest_free
d-i partman/choose_partition select finish
d-i partman/confirm boolean true
d-i partman/confirm_nooverwrite boolean true
d-i partman-md/confirm_nooverwrite boolean true
d-i partman-lvm/confirm_nooverwrite boolean true
d-i partman-partitioning/confirm_write_new_label boolean true
```

You will most likely have to setup your machine to boot in UEFI mode. This differs per Motherboard. It will most likely be in your boot settings.

We run with AsRock H81M-HDS':

Firstly check the Hard Drive is set to AHCI mode.  
`Advanced > Storage Configuration > SATA Mode Selection > AHCI`

Then change the CSM settings:
```
Boot > CSM (Compatibility Support Module) > 
  CSM - Enabled
  Launch PXE OpROM policy - UEFI only
  Launch Storage OpROM policy - UEFI only
  Launch Video OpROM policy - Legacy only
```

## Importing systems from MS DHCP to Cobbler

TODO - Powershell over RPC

Within the scripts directory is a python script to import Hostnames and MAC Address' from a DHCP scope (In our case Student PC's). To avoid AD conflicts it prepends L (for Linux).

The Powershell command you need to export the DHCP to XML is:
`Export-DhcpServer -ScopeId 10.0.72.0 -File dhcp-export.xml -Leases -Force`

To run the python script you need to install `xmltodict`.
```bash
sudo apt-get install python-pip
sudo pip install xmltodict
```

To run the import copy your xml document to your server.
```bash
./dhcp-import.py path/to/file.xml
```

## Configuration management

sudo apt-get install python-pip
sudo pip install fabric
mkdir ~/.ssh
chmod 700 ~/.ssh
ssh-keygen -t rsa

#setup fabric
wget https://raw.github.com/AwaseConfigurations/main/master/scripts/getfabric
chmod u+x getfabric
./getfabric

#generate pair of keys [if absent], put public key to workstations
fab pubkey_distribute

#run fabrics init and main tasks
fab init
fab main


## References

https://wiki.linaro.org/LEG/Engineering/Kernel/UEFI/UEFI_Cobbler  
http://springerpe.github.io/tech/2014/09/09/Installing-Cobbler-2.6.5-on-Ubuntu-14.04-LTS.html  
https://help.ubuntu.com/community/Cobbler/  
http://cobbler.github.io/manuals/quickstart/  
https://help.ubuntu.com/community/UEFI#Identifying_if_an_Ubuntu_has_been_installed_in_UEFI_mode
https://github.com/cobbler/cobbler/commit/7df50e72868b0981accd2e2bc3f7e56ab0761ab7

## TODO

Fix cobblerd init
copy ubuntu.seed
