#!/bin/bash
SUBJECT="Test results"
TO="engrost@gmail.com"
MESSAGE="report.txt"
PROJECT_PATH=/home/django/transact_test/transact
USER=$(whoami)

echo "prepare test project space"
if [ -d $PROJECT_PATH ]; then
    sudo rm -rf $PROJECT_PATH
fi
sudo mkdir -p $PROJECT_PATH
echo "extract project"
sudo tar xzf deploy.tgz -C $PROJECT_PATH
sudo chown -R $USER:$USER $PROJECT_PATH
echo "go to project folder: $PROJECT_PATH"
cd $PROJECT_PATH
#echo "sudo"
#sudo su www-data
screen -X -S transact_test quit
screen -d -S transact_test -m bash --init-file runserver.sh
#./manage.py test --selenium
#run tests
echo "Time: `date`" >> $MESSAGE
./manage.py test >> report.txt 2>&1
#email report
mail -s "$SUBJECT" "$TO" < $MESSAGE
rm runserver.sh
screen -X -S transact_test quit
cd ~
rm deploy.tgz
echo "Deploy done"
