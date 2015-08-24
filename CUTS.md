<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

  - [](#)
- [](#-1)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

 * nginx
  * tftpd-hpa
   * syslinux

unzip netboot.tar.gz in /tftpboot

http://sickbits.net/creating-an-ubuntu-pxe-server/

sudo apt-get install apt-mirror
comment out all deb* lines in /etc/apt/mirror.list and add the following

deb http://archive.ubuntu.com/ubuntu quantal main/debian-installer

or deb-amd64 http://archive.ubuntu.com/ubuntu quantal main/debian-installer for amd64 edition of Ubuntu.
and execute sudo -u apt-mirror apt-mirror

wait a little bit and then copy downloaded files from /var/spool/apt-mirror/mirror/archive.ubuntu.com/ubuntu into your netboot installation point. For example,

cp -a /var/spool/apt-mirror/mirror/archive.ubuntu.com/ubuntu /var/www/

where /var/www has already contained ubuntu directory with dists and pool subdirectories.

wget image
sudo mount -o loop /images/ubuntu-14.04.2-server-amd64.iso /mnt
sudo cp -rf /mnt/* /usr/share/nginx/html/ubuntu/

kickstart file
install/filesystem.squash

add autoindex on; to nginx location /?

write changes to disk?


packages removed:

###
 cobbler-common distro-info distro-info-data fence-agents hardlink
    libapache2-mod-python libgmp10 libnet-telnet-perl libnspr4 libnss3
	     libnss3-nssdb libperl5.18 libsensors4 libsgutils2-2 libsnmp-base libsnmp30
		        powerwake python-cobbler python-crypto python-distro-info python-pexpect
				         python-pyasn1 python-twisted python-twisted-conch python-twisted-lore
						            python-twisted-mail python-twisted-names python-twisted-news
									             python-twisted-runner python-twisted-web python-twisted-words sg3-utils snmp

##

