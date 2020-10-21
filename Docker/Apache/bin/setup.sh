# Install apache and php
apt-get update -q && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -yq software-properties-common apache2 wget md5sum zip unzip python3.8 python3-pip

# Enable mods
a2enmod headers
a2enmod rewrite

# Set time zone
echo "America/Mexico_City" > /etc/timezone
ln -s -f /usr/share/zoneinfo/America/Mexico_City  /etc/localtime

dpkg-reconfigure --frontend noninteractive tzdata

# Restart apache
service apache2 restart
