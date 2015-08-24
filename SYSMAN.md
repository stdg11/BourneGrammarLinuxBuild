# Provisioning and Configuration Management Server

## Build

Start with an install of Ubuntu/Debian Server with OpenSSH Server. We will be using cobbler to build the PXE server.

### Installing Cobbler

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

Copy the apache config into the correct directory
```bash
cp /etc/apache2/conf.d/cobbler.conf /etc/apache2/conf-available/
cp /etc/apache2/conf.d/cobbler_web.conf /etc/apache2/conf-available/
```

Edit tho Cobbler config file `/etc/cobbler/settings`

```bash
server=YOUR-IP
next-server=YOUR-IP
default_password_crypted=SALED-PASSWORD
```

Enable cobbler and reload Apache
```bash
a2enconf cobbler cobbler_web
service apache2 reload
```

change settingt 127.0.0.1 /etc/cobbler/settings
openssl passwd -1 -salt 'random-phrase-here' 'your-password-here'
insert output from above in /etc/cobbler/settings > default_password_crypted: "x"
service apache2 restart
service cobblerd restart
sudo cobbler check
sudo cobbler get-loaders
sudo apt-get install fence-loaders
sudo cobbler sync





###
 cobbler-common distro-info distro-info-data fence-agents hardlink
   libapache2-mod-python libgmp10 libnet-telnet-perl libnspr4 libnss3
     libnss3-nssdb libperl5.18 libsensors4 libsgutils2-2 libsnmp-base libsnmp30
	   powerwake python-cobbler python-crypto python-distro-info python-pexpect
	     python-pyasn1 python-twisted python-twisted-conch python-twisted-lore
		   python-twisted-mail python-twisted-names python-twisted-news
		     python-twisted-runner python-twisted-web python-twisted-words sg3-utils snmp
			 
##

#sudo htdigest /etc/cobbler/users.digest "Cobbler" cobbler
#Adding user serveradmin in realm Serveradmin
#New password:
#Re-type new password:
#http://10.0.72.3/cobbler_web
#sudo cobbler sync
sudo mount -o loop /images/ubuntu-14.04.2-server-amd64.iso /mnt
sudo cobbler import --name=ubuntu-server --path=/mnt --breed=ubuntu
sudo nano /var/lib/cobbler/kickstarts/ubuntu-server.preseed
sudo cobbler reposync
sudo cobbler sync

add 199.27.75.133     www.cobblerd.org cobblerd.org to /etc/hosts
