#!/bin/bash

YEAR=$1
MONTH=$2
DAY=$3

set -e   # set behaviour: exit the script if any command fails

echo "Downloading transactions of the day $YEAR/$MONTH/$DAY"

if test -d "data/DASH-$YEAR-$MONTH-$DAY"; then
    echo "Found a pre-existing folder for this day. I will try to complete it."
else
    echo "I create the folder DASH-$YEAR-$MONTH-$DAY"
    mkdir data/DASH-$YEAR-$MONTH-$DAY
fi


for i in 00 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23
do
    if test -f "data/DASH-$YEAR-$MONTH-$DAY/$i.txt";
    then
        echo "The file with hour $i already exists, I will skip it."
        continue
    else
        python3 download/SoChainDownloader.py "dash" "$YEAR-$MONTH-$DAY-$i:00:00" "$YEAR-$MONTH-$DAY-$i:59:59" "data/DASH-$YEAR-$MONTH-$DAY/$i.txt"
    fi
done

exit(0)
