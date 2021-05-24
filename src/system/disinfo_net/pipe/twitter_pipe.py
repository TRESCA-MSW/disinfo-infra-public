from time import sleep
import os 
import sys
from os.path import dirname, abspath
d = dirname(dirname(abspath(__file__)))
sys.path.insert(0, d)
import logger
import tweepy

from disinfo_net.pipe.domain_pipe import DomainPipe
from disinfo_net.util.domain_util.url_parser import UrlParser

class TwitterPipe(DomainPipe, tweepy.StreamListener):
    def __init__(self, cred_file,terms_file):
        super().__init__()
        self.api = self.initialize_connection(cred_file)
        self.total_tweets = 0
        self.mylogger = logger.get_logger(__name__)
        self.mylogger.debug("terms file="+terms_file)        
        self.terms = self.initialize_terms(terms_file)


    def initialize_terms(self,terms_file):
        """
        Terms must be one-per-line.
        Blank lines will be skipped.
        """
        import codecs
        with codecs.open(terms_file,"r", encoding='utf8') as input:
            # read all the lines
            lines = input.readlines()

            # build a set of terms
            new_terms = ['news']
            for line in lines:
                line = line.strip()
                if len(line):                    
                    new_terms.append(line)        
            return new_terms
        
    def initialize_connection(self, cred_file):
        #creds = self.load_credentials(cred_file)
        C_KEY = os.environ.get('TWITTER_CONSUMER_KEY')
        C_SECRET = os.environ.get('TWITTER_CONSUMER_SECRET')
        A_TOKEN = os.environ.get('TWITTER_TOKEN')
        A_TOKEN_SECRET = os.environ.get('TWITTER_SECRET')

        auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
        auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)

        api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        
        #auth = tweepy.OAuthHandler(creds['consumer_key'],
        #                           creds['consumer_secret'])
        #auth.set_access_token(creds['access_token'],
        #                      creds['access_token_secret'])
        #api = tweepy.API(auth)

        return api

    def run(self):
        try:
            #TODO introduce a more elaborated query, based on specific hashtags -->hashtaglist 
            #stream.filter(track=hash_tag_list)
            #TODO https://github.com/michaelbrooks/twitter-monitor
            myStream = tweepy.Stream(auth=self.api.auth, listener=self)
            terms = ', '.join(['"%s"' % w for w in self.terms])            
            #TODO antes track=['news','filter:links']. Esto funciona, pero no con la lista de términos
            #myStream.filter(track=[terms,"filter:links"],is_async=True)   
            myStream.filter(track=['news','@wakeupfromcovid','@corona_timo','@crismartinj','@JackPosobiec', '@RepMTG','@JosehWolf', '@dangarcar', '@InProportion2','filter:links'])
            
        except Exception as e:
            print(e)
            sleep(60 * 60)

    def on_status(self, status):
        tweet_id = status.id_str
        #print(status.text)               
        
        for url_obj in status.entities['urls']:
            self.total_tweets += 1
            if(self.total_tweets%100==0):
                self.mylogger.debug("USER="+status.user.screen_name)
                self.mylogger.debug("#tweets="+str(self.total_tweets))
            url = url_obj['expanded_url']

            unshortened_url = self.url_parser.unshorten_url(url)
            stripped_url = UrlParser.strip_url(unshortened_url)
            if stripped_url == 'twitter.com':
                continue

            
            self.queue.put((stripped_url, tweet_id, 'twitter'))

    def on_error(self, status_code):
        pass
