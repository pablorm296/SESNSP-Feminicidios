# Enable sites
a2ensite sesnsp.conf

# Disabel default site
a2dissite 000-default.conf

# Restart apache
service apache2 restart

