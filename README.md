## movies_notifier: a simple notifier of new good downloadable movies.

### What is this:
A tool that:
1. Checks what new movies are available for download (from Popcorn-API)
2. Scrapes their ratings from Rotten Tomatoes (gets there by scraping google search).
3. Sends a notification email via Mailgun service if there are any good* movies with their details.

\* good - currently defined as having critics and audience ratings both higher than 80%.


### To run this:
1. Git clone this repo and install requirements (`pip install .` or `pip install -r requirements.txt`)
2. Set up Mailgun account for emailing and put the domain, api-key, and recipients in a json in your `~/.mailgun/mailgun.json` or change the email set-up to whatever suits you (like AWS SES).
4. Run `python check_new_movies.py` or `. cron.sh` or setup a cron-job to run `cron.sh`


### Still to do:
* send full table of new movies as attachment and not only the selected "good" movies.
* add more sophisitcated movie selection logic (perhaps some tiers of relevance).
* scrape ciritics reviews and calculate directly when there are too few reviews for a "tomatometer".
* add CLI for more refined control of parameters.
