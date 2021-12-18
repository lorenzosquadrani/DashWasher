#!/bin/bash

YEAR=2021
MONTH=01
DAY=01

set -e   # set behaviour: exit the script if any command fails

if test -d "DASH-$YEAR-$MONTH-$DAY"; then
    echo "Found a pre-existing folder for this day. I will try to complete it."
else
    echo "I create the folder DASH-$YEAR-$MONTH-$DAY"
    mkdir DASH-$YEAR-$MONTH-$DAY
fi


for i in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
do
    if test -f "DASH-$YEAR-$MONTH-$DAY/$k.txt";
    then
        echo "The file with hour $k - $i already exists, I will skip it."
        continue
    else
        echo "Downloading transactions of the day $YEAR/$MONTH/$DAY"
        ./main.sh "-dlt" "dash" "-start" "$YEAR-$MONTH-$DAY-$i:00:00" "-end" "$YEAR-$MONTH-$DAY-$i:59:59" "-res" "DASH-$YEAR-$MONTH-$DAY/$k.txt"
    fi
done
