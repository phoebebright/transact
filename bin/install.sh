#!/bin/bash
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
mv deployment/* .
#echo "run shells"
#sudo su www-data
screen -X -S transact_server quit
screen -X -S transact_test quit
screen -d -S transact_server -m bash --init-file runserver.sh
screen -d -S transact_test -m bash --init-file runtests.sh
cd ~
rm deploy.tgz
echo "Deploy done, tests are running"
