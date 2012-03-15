#!/bin/bash
SUBJECT="Test results `date`"
TO="engrost@gmail.com"
MESSAGE="report.txt"

#run tests
echo "Start time: `date`" >> $MESSAGE
#./manage.py test --selenium >> $MESSAGE 2>&1
./manage.py test >> $MESSAGE 2>&1

#email report
mail -s "$SUBJECT" "$TO" < $MESSAGE
echo "cleanup"
screen -X -S transact_server quit
screen -X -S transact_test quit