# Twitter-Scraper
## Scrape tweets from Twitter using Twitter API v2

- This is a tool (python script) to search among all tweets and fetch and store data (tweets) from Twitter using Twitter API v2. Also could be easily migrated to v1.1 or any other versions by modifying the `base_url` in `Scraper.py`. For Academic or Premium or Enterprise accounts.
- Best for data gathering for any tweet/textual based analysis.
- Based on https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all

## How to use
Add your bearer_token recieved from Twitter to credentials.py. (just rename credentials.py.sample and replace yours, if you don't have one, get it from here: https://developer.twitter.com/en/docs/twitter-api/getting-started/guide)
Use as demonstraited in main.py:
```python
from Scraper import Scraper

query = "#covid19 OR #pandemic"  # or any other advanced queries
scraper = Scraper(query, results_chunk=500, start_time="2020-03-01T00:00:00Z", end_time="2021-02-016T00:00:00Z")  # or any other parameters from https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
scraper.scrape(max_pages=20)  # fetch 20 pages of 500 tweets (10,000)
```

