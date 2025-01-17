from time import sleep
import praw
import os

from disinfo_net.pipe.domain_pipe import DomainPipe
from disinfo_net.util.domain_util.url_parser import UrlParser

class RedditPipe(DomainPipe):
    def __init__(self, cred_file): 
        super().__init__()
        self.reddit = self.initialize_connection(cred_file)

    def initialize_connection(self, cred_file):
        #creds =  self.load_credentials(cred_file)
        #reddit = praw.Reddit(client_id=creds['client_id'],
        #                     client_secret=creds['client_secret'],
        #                     username=creds['username'],
        #                     password=creds['password'],
        #                     user_agent=creds['user_agent'])
        reddit = praw.Reddit(
            client_id = os.environ.get('REDDIT_CLIENT_ID'),
            client_secret = os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent = os.environ.get('REDDIT_USER_AGENT'),
            username = os.environ.get('REDDIT_USER_NAME'),
            password = os.environ.get('REDDIT_PASSWORD')
        )

        return reddit

    def run(self):
        submissions = 0
        while(1):
            try:
                for submission in self.reddit.subreddit('all').stream.submissions():
                    submissions += 1
                    url = submission.url
                    utc = submission.created_utc
                    post_id = submission.id
                    stripped_url = UrlParser.strip_url(url) 
                    if stripped_url == 'reddit.com' or stripped_url == 'redd.it':
                        continue
                    #print("Reddit stripped="+stripped_url)
                    #print("Reddit-->post_id="+post_id)
                    self.queue.put((stripped_url, post_id, 'reddit'))                    
            except Exception as e:
                print(e)
                sleep(60)
