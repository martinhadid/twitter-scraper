# What is it?
It's a scraper for twitter, it scrapes the feed and stores it into a csv.

# What does it scrape?
It scrapes twitter's news feed for #bitcoin or other hashtags by language for a configurable date range.
Also scrapes users that were displayed in the news feed and its tweets. 
Maintains tweets and users statistics such as likes, retweets and replies.

# How does it work?
To scrape twitter you will have to run python scraper.py defining the following arguments:
- word: hashtag to be searched
- starting date as YYYY-MM-DD
- end date as YYYY-MM-DD
- language from the following option: 'en', 'it', 'es', 'fr', 'de', 'ru', 'zh'
- scraping duration: to be added

Once you have defined your arguments the scraper will build the URL and open a chrome browser for the requested page.
The driver will scroll down for the specified duration and will collect all the tweets' information extracted from the HTML using BeautifulSoup.
After the HTML is retrieved the parser will get each tweet's information including:
- tweet ID
- tweet text
- username
- hashtags
- date  
And some statistics as:
- likes
- replies
- retweets

Having collected all the tweets the scraper will identified all users in the previous tweets and proceed to scrape them.
The driver will navigate to each users homepage and scrape the following data:
- followers
- following
- total tweets
- most recent tweets

All these information will be saved in a MySQL database defined in create_db.sql (which should be previously run). Please configure the database server in the config.py file.
Upon re-scraping Twitter if the scraper finds a previously scraped tweet or user it will update the statistics and save a snapshot of the previous statistics.

