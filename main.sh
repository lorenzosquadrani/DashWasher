#!/bin/bash

YEAR=$1
MONTH=$2
DAY=$3


set -e

bash download/download.sh $YEAR $MONTH $DAY

python3 utilities/file_merger.py -d $YEAR-$MONTH-$DAY

python3 analysis/analyze_transactions_graph.py -c "config.json" -d $YEAR-$MONTH-$DAY

python3 analysis/analyze_random_graph.py -c "config_random.json" -d $YEAR-$MONTH-$DAY
