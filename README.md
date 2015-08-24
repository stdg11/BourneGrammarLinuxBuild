<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Contents**

- [Install Ubuntu](#install-ubuntu)
- [Installed packages](#installed-packages)
- [Bootloader](#bootloader)
- [Boot to command line without X](#boot-to-command-line-without-x)
- [Domain Integration](#domain-integration)
- [Mount users Windows Home Directory](#mount-users-windows-home-directory)
- [Dotfiles](#dotfiles)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Install Ubuntu

Head over to the Ubuntu Download Page and download the latest LTS version.  
Install with defaults, enabling software updates and third party downloads.  
When prompted follow the standard naming convention for hostname and set the username to *linuxadmin*  

## Installed packages

Install the following packages by `sudo apt-get install package-name`  
Alternatively run `cat package-list | xargs sudo apt-get install`  

 * realmd
 * ntp
 * git
 * emacs
 * sssd
 * sssd-tools
 * samba-common-bin
 * libpam-mount
 * cifs-utils

## Bootloader

To make Windows the default Operating System on boot, change your grub config (We have also disabled recovery options):

`sudo nano -B /etc/default/grub`

```bash
# If you change this file, run 'update-grub' afterwards to update
# /boot/grub/grub.cfg.
# For full documentation of the options in this file, see:
#   info -f grub -n 'Simple configuration'

GRUB_DEFAULT=0
#GRUB_HIDDEN_TIMEOUT=0
GRUB_HIDDEN_TIMEOUT_QUIET=true
GRUB_TIMEOUT=10
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
#GRUB_CMDLINE_LINUX_DEFAULT="quiet splash"
GRUB_CMDLINE_LINUX="text"

# Uncomment to enable BadRAM filtering, modify to suit your needs
# This works with Linux (no patch required) and with any kernel that obtains
# the memory map information from GRUB (GNU Mach, kernel of FreeBSD ...)
#GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"

# Uncomment to disable graphical terminal (grub-pc only)
GRUB_TERMINAL=console

# The resolution used on graphical terminal
# note that you can use only modes which your graphic card supports via VBE
# you can see them in real GRUB with the command `vbeinfo'
#GRUB_GFXMODE=640x480

# Uncomment if you don't want GRUB to pass "root=UUID=xxx" parameter to Linux
#GRUB_DISABLE_LINUX_UUID=true

# Uncomment to disable generation of recovery mode menu entries
GRUB_DISABLE_RECOVERY="true"

# Uncomment to get a beep at grub start
#GRUB_INIT_TUNE="480 440 1"

# Default to Windows
GRUB_DEFAULT="Windows 7 (loader) (on /dev/sda1)"

```

**Make sure you run** `sudo update-grub` **after making your changes**

## Boot to command line without X

To boot to the command line run the below command.

`systemctl set-default multi-user.target`

## Domain Integration

To allow Active Directory users to logon you need to install:

 * realmd
 * ntp
 * sssd
 * sssd-tools
 * samba-common-bin
   
Once installed you need to ensure the machines time is the same as the Domain Controllers, this is done by setting the server variable within `/etc/ntp.conf`

```bash
...
server brgradc01.bourne-grammar.lincs.sch.uk
server brgras001.bourne-grammar.lincs.sch.uk
...
```

Once NTP is setup join the machine to the domain using realm

`realm join --user=admin bourne-grammar.lincs.sch.uk`

TODO questions

To allow users to logon without a domain prefix or suffix set `use_fully_qualified_names` to false

`/etc/sssd/sssd.conf`

```bash
[sssd]
domains = bourne-grammar.lincs.sch.uk
config_file_version = 2
services = nss, pam

[domain/bourne-grammar.lincs.sch.uk]
ad_domain = bourne-grammar.lincs.sch.uk
krb5_realm = BOURNE-GRAMMAR.LINCS.SCH.UK
realmd_tags = manages-system joined-with-samba
cache_credentials = True
id_provider = ad
krb5_store_password_if_offline = True
default_shell = /bin/bash
ldap_id_mapping = True
use_fully_qualified_names = False
fallback_homedir = /home/%d/%u
access_provider = ad
```

To allow an Active Directory group administrative rights on the machine add the following sudo entry.

`visudo`

`%linuxadmins ALL=(ALL:ALL) ALL`

## Mount users Windows Home Directory

`/etc/security/pam_mount.conf.xml`

```xml
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE pam_mount SYSTEM "pam_mount.conf.xml.dtd">
<!--
	See pam_mount.conf(5) for a description.
	-->

<pam_mount>

		<!-- debug should come before everything else,
		     	   since this file is still processed in a single pass
			   	      from top-to-bottom -->

<debug enable="0" />

       		  <!-- Volume definitions -->
		  <!-- <volume user="*" fstype="cifs" server="10.0.77.104" path="%(DOMAIN_USER)$" mountpoint="/home/%(DOMAIN_USER)" options="sec=ntlm,nodev,nosuid" /> -->
		  <volume options="username=%(USER),user=%(USER),domain=BRGRA,dir_mode=0700,file_mode=0700" fstype="cifs" server="brgras005.bourne-grammar.lincs.sch.uk" path="%(USER)$" mountpoint="~/Documents"/>
		  	  										    <!-- pam_mount parameters: General tunables -->

<!--
<luserconf name=".pam_mount.conf.xml" />
-->

<!-- Note that commenting out mntoptions will give you the defaults.
     You will need to explicitly initialize it with the empty string
          to reset the defaults to nothing. -->
	  <mntoptions allow="nosuid,nodev,loop,encryption,fsck,nonempty,allow_root,allow_other" />
	  <!--
	  <mntoptions deny="suid,dev" />
	  <mntoptions allow="*" />
	  <mntoptions deny="*" />
	  -->
	  <mntoptions require="nosuid,nodev" />

<logout wait="0" hup="0" term="0" kill="0" />

<!-- pam_mount parameters: Volume-related -->
<mkmountpoint enable="1" remove="true" />
</pam_mount>

```

## Dotfiles

To enable users dotfiles to follow them as they use different machines we came up with the following solution:

Within the students NTFS home directory mounted at `~/Documents` is a folder called dotfiles. Upon logon the program `dotfiles` is run, this symlinks everything within the users `~/Documents/dotfiles` directory and backs up any replaced dotifles. We had to use this method as we encountered numerous issues mounting the students NTFS home directory at `/home/user/`. The NTFS home directory is hosted on a windows file server.

`/usr/bin/dotfiles`

```bash
#!/bin/bash
## Variables
   dot_dir=~/Documents/dotfiles # dotfiles directory
   old_dir=~/Documents/dotfiles/backup # old dotfiles backup directory

   ## Create dotfiles_old
   mkdir -p $old_dir

   ## Change to the dotfiles directory
   cd $dot_dir
   ## Move any existing dotfiles in homedir to dotfiles_old directory,
   ##then create symlinks from the homedir to any files in the dotfiles directory specified in $files
   for file in *; do
       mv ~/.$file $old_dir/
       ln -s $dot_dir/$file ~/.$file
       done									      
```
Reminder: `chmod +x /usr/bin/dotfiles` (Make sure dotfiles is executable)

To ensure `dotfiles` runs on logon after the users home directory is mounted you need to create a desktop entry.

`/etc/xdg/autostart/dotfiles.desktop`

```bash
[Desktop Entry]
Type=Application
Exec=dotfiles
Name=dotfiles
Comment=Copy dotfiles from NTFS home directory
```
