#!/bin/bash
DATA_DIR=$HOME/movies-notifier-data/
docker run --rm -it \
    -v $DATA_DIR:/movies-notifier/data \
    -v $HOME/.config/gspread_pandas/:/root/.config/gspread_pandas/ \
    artdgn/movies-notifier -g your-email@gmail.com

