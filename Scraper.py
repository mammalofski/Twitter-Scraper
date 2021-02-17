import requests
import pandas as pd
from datetime import datetime
from credentials import bearer_token  # bearer token for your Twitter account should be stored here


class TweetStorage:
    def __init__(self):
        self.attributes = ['id', 'text', 'hashtags', 'created_at', 'geo', 'like_count', 'quote_count', 'reply_count',
                           'retweet_count']
        self._data_frame = pd.DataFrame(columns=self.attributes)
        self.file_name = "tweets_{}.csv".format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

    def save_tweets(self, jason_response):
        processed_tweets = self.process_tweets(jason_response)
        self.add_tweets_to_data_frame(processed_tweets)

    def process_tweets(self, jason_response):
        tweets = list()
        for tweet in jason_response['data']:
            hashtags = " ".join([tag['tag'] for tag in tweet.get('entities', {}).get('hashtags', [])])
            processed_tweet = (tweet['id'], tweet['text'], hashtags, tweet['created_at'], tweet.get('geo', ''),
                               tweet['public_metrics']['like_count'], tweet['public_metrics']['quote_count'],
                               tweet['public_metrics']['reply_count'], tweet['public_metrics']['retweet_count'])
            tweets.append(processed_tweet)
        return tweets

    def add_tweets_to_data_frame(self, tweets):
        new_df = pd.DataFrame(tweets, columns=self.attributes)
        self._data_frame = self._data_frame.append(new_df)

    def store(self, description=''):
        print('exporting as csv ... ')
        self._data_frame.index.name = 'index'
        self._data_frame.to_csv(self.file_name)
        # write the description for the existing gathered data
        description_file = open('description_{}.txt'.format(self.file_name), 'w+')
        description += "\n\nheaders: {}\ndata_shape: {}\nfor file: {}".format(self.attributes, self._data_frame.shape,
                                                                              self.file_name)
        description_file.write(description)
        description_file.close()


class Scraper:
    def __init__(self, query, results_chunk=10, **kwargs):
        self.query = query
        self.results_chunk = results_chunk
        # other kwargs will go to the request url directly
        self._kwargs = kwargs  # TODO: kwargs should be validated

        self._base_url = "https://api.twitter.com/2/tweets/search/all"
        self._headers = self._create_headers(bearer_token)

        self.tweet_storage = TweetStorage()

    def create_url(self, query, max_results=10, **kwargs):
        tweet_fields = "tweet.fields=created_at,geo,text,public_metrics"
        url = "{}?query={}&max_results={}&{}".format(self._base_url, query, max_results, tweet_fields)
        # add any more given parameters to the url's query params
        for key, value in kwargs.items():
            if value:
                url += "&{}={}".format(key, value)
        return url

    def make_request(self, url):
        response = requests.request("GET", url, headers=self._headers)
        print('The response status code: ', response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        return response.json()

    def _create_headers(self, bearer_token):
        headers = {"Authorization": "Bearer {}".format(bearer_token)}
        return headers

    def save_tweets(self, jason_response):
        self.tweet_storage.save_tweets(jason_response)

    def retrieve_pages(self, max_pages):
        # if `pages` is None, it will retrieve EVERYTHING matching query
        # init loop variables:
        page = 1
        current_page_url = self.create_url(self.query, max_results=self.results_chunk,
                                           **self._kwargs)  # the initial url containing the query
        while max_pages is not None and page <= max_pages:
            jason_response = self.make_request(current_page_url)

            self.save_tweets(jason_response)

            next_token = jason_response['meta'].get('next_token')
            if not next_token:  # if twitter has no further tweets, then it's enough
                break

            page += 1
            current_page_url = self.create_url(self.query, max_results=self.results_chunk, next_token=next_token,
                                               **self._kwargs)

    def scrape(self, max_pages=2):
        try:
            self.retrieve_pages(max_pages)
        finally:
            description = "query: {} \nkwargs: {}".format(self.query, self._kwargs)
            self.tweet_storage.store(description)


