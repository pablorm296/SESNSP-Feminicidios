FROM ubuntu:latest

# Set time zone
ENV TZ=America/Mexico_City

# Makee sure we are in /root/
WORKDIR /root/

# Copy bin dir
COPY bin .

# Copy config dir
COPY config .

# Run setup script
RUN ./setup.sh

# Copy apache config files
RUN ["cp", "./apache2.conf", "/etc/apache2/apache2.conf"]
RUN ["cp", "./sesnsp.conf", "/etc/apache2/sites-available/"]

# Create server directories
RUN ["mkdir", "-p", "/var/www/SESNSP"]
RUN ["mkdir", "-p", "/var/www/SESNSP/FullPage"]
RUN ["mkdir", "-p", "/var/www/SESNSP/Docs"]
RUN ["mkdir", "-p", "/srv/SESNSP"]

# Run second setup script
RUN ./setup_2.sh

# Expose port 80 (Apache)
EXPOSE 80

# Run apache
CMD apache2ctl -D FOREGROUND
