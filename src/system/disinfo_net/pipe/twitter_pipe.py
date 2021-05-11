from time import sleep
import os 

import tweepy

from disinfo_net.pipe.domain_pipe import DomainPipe
from disinfo_net.util.domain_util.url_parser import UrlParser

class TwitterPipe(DomainPipe, tweepy.StreamListener):
    def __init__(self, cred_file):
        super().__init__()
        self.api = self.initialize_connection(cred_file)
        self.total_tweets = 0

    def initialize_connection(self, cred_file):
        #creds = self.load_credentials(cred_file)
        C_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
        C_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
        A_TOKEN = os.environ.get('TWITTER_TOKEN')
        A_TOKEN_SECRET = os.environ.get('TWITTER_SECRET')

        auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
        auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

        api = tweepy.API(auth)
        
        #auth = tweepy.OAuthHandler(creds['consumer_key'],
        #                           creds['consumer_secret'])
        #auth.set_access_token(creds['access_token'],
        #                      creds['access_token_secret'])
        #api = tweepy.API(auth)

        return api

    def run(self):
        try:
            myStream = tweepy.Stream(auth=self.api.auth, listener=self)
            myStream.filter(track=['news', 'filter:links'])            
        except Exception as e:
            print(e)
            sleep(60 * 60)

    def on_status(self, status):
        tweet_id = status.id_str
        for url_obj in status.entities['urls']:
            self.total_tweets += 1
            url = url_obj['expanded_url']

            unshortened_url = self.url_parser.unshorten_url(url)
            stripped_url = UrlParser.strip_url(unshortened_url)
            if stripped_url == 'twitter.com':
                continue

            print("Twitter stripped="+stripped_url)
            print("Twitter-->post_id="+post_id)
            self.queue.put((stripped_url, tweet_id, 'twitter'))

    def on_error(self, status_code):
        pass
