<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Contents**

- [Prerequisites](#prerequisites)
- [Installing Cobbler](#installing-cobbler)
- [Setup cobbler-web](#setup-cobbler-web)
- [Adding Ubuntu Server image to Cobbler](#adding-ubuntu-server-image-to-cobbler)
- [References](#references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Prerequisites

Start with an install of Ubuntu/Debian Server with OpenSSH Server.

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


sudo nano /var/lib/cobbler/kickstarts/ubuntu-server.preseed
sudo cobbler reposync
sudo cobbler sync


## References

https://wiki.linaro.org/LEG/Engineering/Kernel/UEFI/UEFI_Cobbler  
http://springerpe.github.io/tech/2014/09/09/Installing-Cobbler-2.6.5-on-Ubuntu-14.04-LTS.html  
https://help.ubuntu.com/community/Cobbler/  
http://cobbler.github.io/manuals/quickstart/  
