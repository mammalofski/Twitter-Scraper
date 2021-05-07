# Twitter-Scraper
## Scrape tweets from Twitter using Twitter API v2 handling 429 too many requests error

- This is a tool (python script) to search among all tweets and fetch and store data (tweets) from Twitter using Twitter API v2. Also could be easily migrated to v1.1 or any other versions by modifying the `base_url` in `Scraper.py`. For Academic, Premium or Enterprise accounts.
- Best for massive data gathering for any tweet/textual based analysis.
- Based on https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
- **Handles 429 too many requests error** using `x-rate-limit-reset` header. (waits the exact amount of time it should until the throttling resets and continues)

## How to use
Add your bearer_token recieved from Twitter to credentials.py. (just rename credentials.py.sample to credentials.py and replace yours, if you don't have one, get it from here: https://developer.twitter.com/en/docs/twitter-api/getting-started/guide)
Use as demonstraited in main.py (you could simply update the query and the parameters in the main.py and run it: `$ python3 main.py`):
```python
from Scraper import Scraper

query = "#covid19 OR #pandemic"  # or any other advanced queries
scraper = Scraper(query, results_chunk=500, start_time="2020-03-01T00:00:00Z", end_time="2021-02-016T00:00:00Z")  # or any other parameters from https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
scraper.scrape(max_pages=20)  # fetch 20 pages of 500 tweets (10,000)
```
After running, it saves 2 files, a csv containing the flattened data (the columns are the `self.attributes` in `TweetStorage` class) and a txt file containing the description of the data.

### Optional
- you could set the `store_raw_requests` to `True` to store the raw request bodies (non-flattened) as well in a third file.
- you could add any other parameters from https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all to the Scraper object to filter your search

## How to Personalize
in `Scraper.py`:
- To modify the fields: Update the `tweet_fields` variable in `create_url` method in the `Scraper` class and `self.attributes` in `TweetStorage` class according to your needs. (the `process_tweets` method flattenes the data, so modify it according to `tweet_fields`)
- To use other API endpoints: Update the `base_url` in `Scraper` class and to use other API endpoints or to migrate to other versions of Twitter API.


