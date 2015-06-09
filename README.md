# Bourne Grammar School Student Linux PC Build

## TODO

 * Foreman server build machine
 * Script to copy configs
 * startx
 * lynx/stema train thing
 * hide users
 * link home

## Install Ubuntu

Head over to the Ubuntu Download Page and download the latest LTS version.  
Install with defaults, enabling software updates and third party downloads.  
When prompted follow the standard naming convention for hostname and set the username to *linuxadmin*  

## Install packages

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

## Copy configs

## Bind


`realm join --user=admin bourne-grammar.lincs.sch.uk`

## sudo

`visudo`

`%linuxadmins ALL=(ALL:ALL) ALL`

## /etc/sssd/sssd.conf

Allow user to logon without Domain Suffix/Prefix

`use_fully_qualified_names = False`

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
