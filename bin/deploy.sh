#!/bin/bash
if [ -f deploy.tgz ]; then
    rm deploy.tgz
fi
#remove pyc files
find -name ".pyc" -exec rm {} \;
#pack all
tar czf deploy.tgz api libs media site_media templates utils web webtest manage.py settings.py urls.py deployment
scp deploy.tgz transact.trialflight.com:
ssh transact.trialflight.com 'bash -s' < bin/install.sh
rm deploy.tgz