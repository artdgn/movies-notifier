## movies_notifier: a simple notifier of new good downloadable movies.

### What is this:
A tool that:
1. Checks what new movies are available for download (from Popcorn-API)
2. Scrapes their ratings from Rotten Tomatoes (gets there by scraping google search).
3. Sends a notification email via Mailgun service if there are any good* movies with their details.

\* good - currently defined as having critics and audience ratings both higher than 80%.


### To run this:
1. Git clone this repo and install requirements (`pip install .` or `pip install -r requirements.txt`) preferrably in a python3.6 venv/conda.
2. Set up Mailgun account for emailing and put the domain, api-key, and recipients in a json in your `~/.mailgun/mailgun.json` or change the email set-up to whatever suits you (like AWS SES) or do whatever else you like with the output.
4. Run `python check_new_movies.py` or `. cron.sh` (check you're using the right python path) or setup a cron-job to run `cron.sh`


### Still to do:
* use AWS free tier to store full table (S3 and link in email / API in lambda + dynamo)
* rescrape previous scrapes to check if RT data added (might happen for newer movies)
* add more sophisitcated movie selection logic (perhaps some tiers of relevance).
* scrape ciritics reviews and calculate directly when there are too few reviews for a "tomatometer".
* add CLI for more refined control of parameters.


#### Tools and references for development:
- scraping: [Scrapy](https://docs.scrapy.org/en/latest/)
- scraping: [Selector Gadget](https://selectorgadget.com/)
- torrents: [Popcorn-API docs](https://popcornofficial.docs.apiary.io/#)
- emails: [Mailgun examples](https://documentation.mailgun.com/en/latest/api-sending.html#examples)
