# Install apache and php
apt-get update -q && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install -yq software-properties-common apache2 wget coreutils zip unzip python3.8 python3-pip git

# Install virtualenv
pip3 install virtualenv

# Enable mods
a2enmod headers
a2enmod rewrite

# Create a copy of the repo
git clone https://github.com/pablorm296/SESNSP-Feminicidios.git

# Set time zone
echo "America/Mexico_City" > /etc/timezone
ln -s -f /usr/share/zoneinfo/America/Mexico_City  /etc/localtime

dpkg-reconfigure --frontend noninteractive tzdata

# Restart apache
service apache2 restart
