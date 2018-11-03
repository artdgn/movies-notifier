#!/usr/bin/env bash
HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd $HERE/..
docker build -t movies_notifier .
docker run --rm -v $HERE/..:/movies_notifier movies_notifier "$@"