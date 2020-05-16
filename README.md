## movies-notifier: a simple notifier of new good downloadable movies.

### What is this:
A tool that:
1. Checks what new movies are available for download (from Popcorn-API)
2. Checks their ratings on Rotten Tomatoes (gets there by scraping search results).
3. Sends a notification if there are any good* movies with their details. 
Currently two types of notifications supported:
    - Upload and share via Google Sheets (requires Google Sheets API setup).
    - Email via Mailgun (requires Mailgun API setup).

\* good - currently defined as having critics and audience ratings average higher than 80%.


### To run this:

#### With docker:
1. Create a directory for local storage (between runs), e.g. `mkdir ~/your_movies_data`.  
2. Run using `docker run --rm -v ~/your_movies_data:/movies-notifier/data artdgn/movies-notifier`. 
    - With no command line options this will just print the help message.
    - Specify number of movies to scan e.g. `-n 100` to scan, select good movies, and print to screen.
        
> Optional: setup Mailgun** acount or Google Sheets API access*** if you want to send notification emails.
 Setup a cron job to do that (example in `scripts/example_cron.sh`) 

#### Using local installation
1. Git clone this repo and install requirements in a virtual env using `make install`.
3. Run: `python run_cli.py`. 

##### \** Setting up Mailgun: 
after setting up the account, put the domain, api-key, and recipients in a 
    json in `movies-notifier/data/mailgun/mailgun.json` or just run and check the error message for exact instructions. 

##### \*** Setting up Google Sheets API
Refer to the setup in 
[gspread-pandas](https://github.com/aiguofer/gspread-pandas) or [gspread](https://github.com/burnash/gspread)
and than run with `-g your-email@gmail.com` to recieve a share notification with the resulting doc.

### To do:
* "Directed by" field
* better ranking using past labels from the notification google-sheet
* replace google scraping with `googler -w rottentomatoes -n 10 --json` ([Googler](https://github.com/jarun/googler#installation)
* add more sophisitcated movie selection logic (perhaps some tiers of relevance).


#### Tools and references for development:
- scraping: [Scrapy](https://docs.scrapy.org/en/latest/)
- scraping: [Selector Gadget](https://selectorgadget.com/)
- torrents: [Popcorn-API docs](https://popcornofficial.docs.apiary.io/#)
- emails: [Mailgun examples](https://documentation.mailgun.com/en/latest/api-sending.html#examples)
- google sheets: [gspread](https://github.com/burnash/gspread) and [gspread-pandas](https://github.com/aiguofer/gspread-pandas)
