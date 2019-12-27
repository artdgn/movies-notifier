## movies-notifier: a simple notifier of new good downloadable movies.

### What is this:
A tool that:
1. Checks what new movies are available for download (from Popcorn-API)
2. Checks their ratings on Rotten Tomatoes (gets there by scraping search results).
3. Sends a notification email via Mailgun service if there are any good* movies with their details.

\* good - currently defined as having critics and audience ratings average higher than 80%.


### To run this:

#### With docker:
1. Create a directory for local storage (between runs), e.g. `mkdir ~/your_movies_data`.
2. Optional: setup Mailgun** acount if you want to send notification emails, or use `-ne` option 
    to just print them out.
3. run using `docker run --rm -v ~/your_movies_data:/movies-notifier/data artdgn/movies-notifier`, 
    with no command line options this will just print the help message, 
    or add e.g. `-n 100 -ne` to that line to scan last 100 movies and print the notifications to screen.

#### Using local installation
1. Git clone this repo and install requirements (`pip install .` or `pip install -r requirements.txt`) 
    preferrably in a python3.6 venv/conda.
2. Optional: set up Mailgun account** for emailing or just print the notifications with the `-ne` option.
3. Run:
    - `python check_new_movies.py` or 
    - `. scripts/cron.sh` (check you're using the right python path) or 
    - setup a cron-job to run `scripts/cron.sh`

\** setting up Mailgun: after setting up the account, put the domain, api-key, and recipients in a 
    json in `movies-notifier/data/mailgun/mailgun.json` or just run and check the error message for exact instructions. 


### Still to do:
* replace google scraping with `googler -w rottentomatoes -n 10 --json` ([Googler](https://github.com/jarun/googler#installation)
* add more sophisitcated movie selection logic (perhaps some tiers of relevance).


#### Tools and references for development:
- scraping: [Scrapy](https://docs.scrapy.org/en/latest/)
- scraping: [Selector Gadget](https://selectorgadget.com/)
- torrents: [Popcorn-API docs](https://popcornofficial.docs.apiary.io/#)
- emails: [Mailgun examples](https://documentation.mailgun.com/en/latest/api-sending.html#examples)
- google sheets: [gspread](https://github.com/burnash/gspread) and [gspread-pandas](https://github.com/aiguofer/gspread-pandas)
