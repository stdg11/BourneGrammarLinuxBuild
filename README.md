# Bourne Grammar School Student Linux PC Build

## Install Ubuntu

Head over to the Ubuntu Download Page and download the latest LTS version.  
Install with defaults, enabling software updates and third party downloads.  
When prompted follow the standard naming convention for hostname and set the username to *linuxadmin*  

## Install packages

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

## /etc/security/pam_mount....
