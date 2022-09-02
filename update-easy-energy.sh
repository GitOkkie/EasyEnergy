#!/bin/bash 

# run dit vanuit je favoriete cron-variant, bijvoorbeeld:
# 10 * * * * /usr/local/bin/update-easy-energy.sh

$DOCROOT=/var/www/html/
$EASYAPI=/usr/local/bin/easyapi.py

cd $DOCROOT || exit 1

$EASYAPI > ee.new 

# crontab mailt me als er nieuwe data is
diff -u ee.txt ee.new | grep ^+[^+]
mv -f ee.new ee.txt
