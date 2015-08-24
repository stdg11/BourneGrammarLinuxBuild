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
