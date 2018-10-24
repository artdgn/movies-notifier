#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $DIR
echo "popcorn notifier" $(date) >> $HOME/cron.log 2>&1
$HOME/miniconda3/bin/python check_new_movies.py >> $HOME/cron.log 2>&1
