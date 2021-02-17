from Scraper import Scraper

if __name__ == "__main__":
    query = "#covid19 OR #pandemic"  # or any other advanced queries
    scraper = Scraper(query, results_chunk=500, start_time="2020-03-01T00:00:00Z", end_time="2021-02-016T00:00:00Z")  # or any other parameters from https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-all
    scraper.scrape(max_pages=20)  # fetch 20 pages of 500 tweets (10,000)