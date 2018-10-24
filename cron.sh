#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $DIR
echo "popcorn notifier" $(date) &>> ~/cron.log
$(realpath ~/miniconda3/bin/python) check_new_movies.py &>> ~/cron.log