#!/bin/bash

mkdir -p "%root%/etc/apache"
# Configure Apache for WebDAV with a new file in the /etc/apache2/sites-available directory:
#cat <<"EOF" > "%root%/etc/apache2/sites-available/webdav.conf"
cat <<"EOF" > "%root%/etc/apache/webdav.conf"
DocumentRoot /var/www/webdav

Alias /webdav /var/www/webdav

<Directory /var/www/webdav>
    Options Indexes FollowSymLinks
    AllowOverride AuthConfig
    Dav On
    AuthType Digest
    AuthName "ums"
    AuthUserFile "/wfs/apache/.htdigest"
    Require user igel
</Directory>
EOF

cat <<"EOF" > "%root%/etc/apache/apache-init.sh"
#!/bin/bash
#set -x
#trap read debug

ACTION="apache_${1}"

# App Path
APP_PATH="/services/apache"
APP_RW_PATH="/services_rw/apache"
APP_WWW_PATH="/var/www"
APP_WEBDAV_PATH="/var/www/webdav"
APP_USR_SBIN="${APP_PATH}/usr/sbin"

LOGGER="logger -it ${ACTION}"

# link ${APP_USR_SBIN} into file system
# Linking files and folders on proper path
find ${APP_PATH}/usr/sbin -printf "/%P\n" | while read DEST
do
  if [ ! -z "/usr/sbin/${DEST}" -a ! -e "/usr/sbin/${DEST}" ]; then
    # Remove the last slash, if it is a dir
    [ -d /usr/sbin/$DEST ] && DEST=${DEST%/} | $LOGGER
    if [ ! -z "/usr/sbin/${DEST}" ]; then
      ln -sv "${APP_PATH}/usr/sbin/${DEST}" "/usr/sbin/${DEST}" | $LOGGER
    fi
  fi
done

# Use /wfs/apache for files
if [ ! -d /wfs/apache ]; then
mkdir -p /wfs/apache
cp /etc/apache/webdav.conf /wfs/apache
fi
ln -svf /wfs/apache/webdav.conf /etc/apache2/sites-available/webdav.conf

#enable_default_mpm
a2enmod -m -q mpm_event | $LOGGER

# refresh_modules
a2enmod -q proxy_html | $LOGGER

# install_default_files
mkdir -p ${APP_WWW_PATH}
ln -svf ${APP_RW_PATH}/${APP_WEBDAV_PATH} ${APP_WEBDAV_PATH} | $LOGGER
if [ ! -e ${APP_WEBDAV_PATH/index.html} ]; then
cp /services/apache/usr/share/apache2/default-site/index.html /var/www/html/index.html | $LOGGER
fi

# enable_default_modules
for module in authz_host auth_digest access_compat authn_file authz_user \
    alias dir autoindex \
    env mime negotiation setenvif \
    filter deflate \
    status reqtimeout ; do
  a2enmod -m -q $module | $LOGGER
done

# enable_default_conf
for conf in charset localized-error-pages other-vhosts-access-log \
    security serve-cgi-bin ; do
  a2enconf -m -q $conf | $LOGGER
done

# install_default_site
a2ensite -q 000-default | $LOGGER

mkdir -p /var/log/apache2
touch /var/log/apache2/error.log /var/log/apache2/access.log | $LOGGER
chown 0:0 /var/log/apache2/error.log /var/log/apache2/access.log | $LOGGER
chmod 0640 /var/log/apache2/error.log /var/log/apache2/access.log | $LOGGER

touch /var/log/apache2/other_vhosts_access.log | $LOGGER
chown 0:0 /var/log/apache2/other_vhosts_access.log | $LOGGER
chmod 0640 /var/log/apache2/other_vhosts_access.log | $LOGGER

# execute_deferred_actions
# not done

# WebDAV functionality requires specific Apache modules
a2enmod dav | $LOGGER
a2enmod dav_fs | $LOGGER
a2enmod auth_digest | $LOGGER

#Create a Directory for WebDAV ${APP_WEBDAV_PATH}
chown -R 0:0 ${APP_RW_PATH}${APP_WEBDAV_PATH} | $LOGGER
chmod -R 755 ${APP_RW_PATH}${APP_WEBDAV_PATH} | $LOGGER
#ln -svf ${APP_RW_PATH}${APP_WEBDAV_PATH} ${APP_WEBDAV_PATH} | $LOGGER

#Enable the WebDAV Site
a2ensite webdav.conf | $LOGGER

#systemctl restart apache2


echo "Finished" | $LOGGER

EOF