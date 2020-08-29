![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/artdgn/movies-notifier?label=dockerhub&logo=docker)
# movies-notifier
### A simple notifier of new good downloadable movies.

1. Checks what new movies are available for download (from Popcorn-API)
2. Checks their ratings on Rotten Tomatoes (gets there by scraping search results).
3. Sends a notification if there are any good* movies with their details. 
Currently two types of notifications supported:
    - Upload and share via Google Sheets (requires Google Sheets API setup).
    - Email via Mailgun (requires Mailgun API setup).
    - No notification: just standard output and save a timestamped HTML table in `./data/html/`

\* good - currently defined as having critics and audience ratings average higher than 80%.

Google Sheets auto-sharing:

![](https://artdgn.github.io/images/movies-notifier.png)


## Usage:

<details><summary>Docker options</summary>

1. Create a directory for local storage (between runs), e.g. `mkdir ~/your_movies_data`.  
2. Run using `docker run --rm -v ~/your_movies_data:/movies-notifier/data artdgn/movies-notifier`. 
    - With no command line options this will just print the help message.
    - Specify number of movies to scan e.g. `-n 100` to scan, select good movies, and print to screen.
    
</details>
        
<details><summary>Local python option</summary>

1. Git clone this repo and install requirements in a virtual env using `make install`.
3. Run: `python run_cli.py`. 

</details>

## Notifications (Optional):

<details><summary>Setting up posting notificaiton to a Google Sheets</summary>

Refer to the setup in 
[gspread-pandas](https://github.com/aiguofer/gspread-pandas) or [gspread](https://github.com/burnash/gspread)
and than run with `-g your-email@gmail.com` to recieve a share notification with the resulting doc.

</details>

<details><summary>Setting up Mailgun for email notifications</summary>
 
After setting up the account, put the domain, api-key, and recipients in a 
    json in `movies-notifier/data/mailgun/mailgun.json` or just run and check the error message for exact instructions. 
</details>

<details><summary>Scheduling</summary>

Setup a cron job to scan and notify periodically (example script to point the cron at: `scripts/example_cron.sh`)

</details>

## Tools and references for development:
<details><summary>Refences</summary>

- scraping: [Scrapy](https://docs.scrapy.org/en/latest/)
- scraping: [Selector Gadget](https://selectorgadget.com/)
- torrents: [Popcorn-API docs](https://popcornofficial.docs.apiary.io/#)
- emails: [Mailgun examples](https://documentation.mailgun.com/en/latest/api-sending.html#examples)
- google sheets: [gspread](https://github.com/burnash/gspread) and [gspread-pandas](https://github.com/aiguofer/gspread-pandas)
</details>