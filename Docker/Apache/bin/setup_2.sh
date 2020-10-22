# Enable sites
a2ensite sesnsp.conf

# Disabel default site
a2dissite 000-default.conf

# Restart apache
service apache2 restart

# Run install script
(cd /srv/SESNSP && bash setup.bash)

# Enable cron service
systemctl enable cron

# Register cron jobs
crontab /srv/SESNSP/sesnsp.chron
