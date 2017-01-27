#!/bin/bash
echo "sendattach hourly cron ran top">>/var/tmp/hourly.txt
python ~filatei/git/googdev/mailbox2csv.py -b fcmb
python ~filatei/git/googdev/mailbox2csv.py -b gtbank
python ~filatei/git/googdev/mailbox2csv.py -b stanbic

FOLDER=/var/tmp/BANKS
SWITCH=""
# Send the most recent 3 files
for file in `ls -t $FOLDER | head -n3 |awk '{printf(" %s\n",$0)}'`
do
 SWITCH="$SWITCH  -a  $FOLDER/$file"
done
# ls -t $FOLDER | head -n3 |awk '{printf(" %s\n",$0)}'
#  echo $SWITCH

DATE=`date`
echo " Teller Record for the Hour $DATE " |mailx $SWITCH -s "Teller Records for the Hour" fidoaccounts@gtsng.com
date >>/var/tmp/hourly.txt
echo "sendattach hourly cron ran $DATE ">>/var/tmp/hourly.txt
