import requests
import pandas as pd
from datetime import datetime
from credentials import bearer_token  # bearer token for your Twitter account should be stored here
import time
import urllib


class TweetStorage:
    def __init__(self, store_raw_requests=False):
        self.attributes = ['id', 'text', 'hashtags', 'created_at', 'geo', 'like_count', 'quote_count', 'reply_count',
                           'retweet_count']
        self._data_frame = pd.DataFrame(columns=self.attributes)
        self.file_name = "tweets_{}.csv".format(datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S'))

        self.store_raw_requests = store_raw_requests
        self.raw_requests_file = None
        if self.store_raw_requests:
            self.raw_requests_file = open(self.file_name + '_raw.txt', 'a+')

    def save_tweets(self, jason_response):
        if self.store_raw_requests:
            self.raw_requests_file.write(jason_response + "\n\n")

        processed_tweets = self.process_tweets(jason_response)
        self.add_tweets_to_data_frame(processed_tweets)

    def process_tweets(self, jason_response):
        tweets = list()
        for tweet in jason_response['data']:
            hashtags = " ".join(['#' + tag['tag'] for tag in tweet.get('entities', {}).get('hashtags', [])])
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

        if self.store_raw_requests:
            self.raw_requests_file.close()


class Scraper:
    def __init__(self, query, results_chunk=10, log=False, **kwargs):
        self.query = query
        self.results_chunk = results_chunk
        # other kwargs will go to the request url directly
        self._kwargs = kwargs  # TODO: kwargs should be validated
        self.log = log

        self._base_url = "https://api.twitter.com/2/tweets/search/all"
        self._headers = self._create_headers(bearer_token)

        self.tweet_storage = TweetStorage()

    def create_url(self, query, max_results=10, **kwargs):
        query = urllib.parse.quote(query)
        tweet_fields = "tweet.fields=created_at,geo,text,public_metrics"
        url = "{}?query={}&max_results={}&{}".format(self._base_url, query, max_results, tweet_fields)
        # add any more given parameters to the url's query params
        for key, value in kwargs.items():
            if value:
                url += "&{}={}".format(key, value)
        return url

    def make_request(self, url):
        if self.log:
            print('requesting', url)
        response = requests.request("GET", url, headers=self._headers)
        if self.log:
            print('The response status code: ', response.status_code)
        if response.status_code != 200:
            # raise Exception(
            #     "Request returned an error: {} {}".format(
            #         response.status_code, response.text
            #     )
            # )
            print('error requesting', url)
            print('the status code is', response.status_code, 'the message is', response.text)
        return response

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
        if self.log:
            print('starting to fetch tweets, the base url is: ', current_page_url)

        error_try_count = 0
        while not max_pages or max_pages is not None and page <= max_pages:
            if self.log:
                print('retrieving page', page, '...')

            response = self.make_request(current_page_url)

            if response.status_code == 200:  # if the request was successful
                jason_response = response.json()
                self.save_tweets(jason_response)

                next_token = jason_response['meta'].get('next_token')
                if not next_token:  # if twitter has no further tweets, then it's enough
                    print('no more tweets left to retrieve...')
                    break

                page += 1
                current_page_url = self.create_url(self.query, max_results=self.results_chunk, next_token=next_token,
                                                   **self._kwargs)
                error_try_count = 0
                time.sleep(1)  # to prevent the 1 sec throttling

            # if request was not successful, then handle errors:
            elif response.status_code == 429:  # too many requests
                try:
                    print('too many requests ... ')
                    print('the header is ', response.headers)
                    throttle_end_timestamp = int(response.headers.get('x-rate-limit-reset'))
                    throttle_end_time = datetime.strftime(datetime.fromtimestamp(throttle_end_timestamp), "%H:%M:%S")
                    time_to_wait = int(throttle_end_timestamp - datetime.now().timestamp()) + 5
                    print('lets rest for', time_to_wait, 'seconds and wake up at', throttle_end_time)
                    print('sleeping ...')
                    time.sleep(time_to_wait)
                except:
                    print('lets rest for 3 minutes and try again...')
                    error_try_count += 1
                    time.sleep(60 * 3)  # if the original waiting plan failed, sleep for 3 minutes before trying
                finally:
                    pass  # to prevent closing the app if it terminates in the except block for any reason e.g. manually

                continue

            else:
                print('unhandled error, try again in 5 minutes')
                time.sleep(5 * 60)
                error_try_count += 1

                if error_try_count == 10:
                    message_from_admin = input('tried for 10 times and failed due to the error shown above, try again? y/n')
                    if message_from_admin == 'y':
                        error_try_count = 0
                    else:
                        break

                continue



    def scrape(self, max_pages=2):
        try:
            self.retrieve_pages(max_pages)
        except:
            print('program failed at some point, saving everything so far...')
        finally:
            description = "query: {} \nkwargs: {}".format(self.query, self._kwargs)
            self.tweet_storage.store(description)
