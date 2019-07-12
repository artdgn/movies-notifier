#!/bin/bash
echo "popcorn notifier" $(date) >> $HOME/cron.log 2>&1
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $HERE/..
$(make python) check_new_movies.py >> $HOME/cron.log 2>&1
