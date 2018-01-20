# A1-1 Use Twitter Streaming API to collect tweets and reprocess
# A1-2 Store processed tweets to ElasticSearch
# We processed tweets to store only the id, screen name, created time, geo coordinates, and tweet text.
# Import the necessary methods from tweepy library
import json, time, tweepy, certifi, elasticsearch
from codecs import open
from dateutil import parser
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler, Stream
from elasticsearch import Elasticsearch

# Variables that contains the user credentials to access Twitter API
consumer_key = 'IKjeC90tREsuG9cDyBI4ced67'
consumer_secret = 'W4nJoFD38jL1qLn6qH11kwHfwPeMJsq9cCgwXe3cgCUo6ZjOSp'
access_token = '919202142275153920-DLKBq1sPF6XcHE3R4PdG5jhwxxVOVf6'
access_token_secret = 'sADP7E4Xny4RA50wZK287hUlzraVG19VsweX1H47NJrpV'

# Elasticsearch endpoint
ep = "https://search-twittmap2-wyrpney5f6kj5lgndhaysbbdhy.us-east-1.es.amazonaws.com"

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
timeformat = '%Y-%m-%dT%H:%M:%SZ'
# Append function
def appendlg(f,s):
    f.write(u'[{0}] \n'.format(time.strftime(timeformat),s))
    f.flush()

# References:
# http://docs.tweepy.org/en/v3.4.0/streaming_how_to.html
# http://adilmoujahid.com/posts/2014/07/twitter-analytics/
class MyStreamListener(StreamListener):
    def __init__(self, es, f):
        super(MyStreamListener, self).__init__()
        self.es = es
        self.f = f

    def on_data(self, data):
        try:                                # A1-1: Process streamed tweets
            d_data = json.loads(data)       # Decode the data
            geo = d_data.get('coordinates') # Google map accessible tag
            if geo:
                tweet_id = d_data['id_str']
                tweet = {
                    'user': d_data['user']['screen_name'],
                    'text': d_data['text'],
                    'geo': geo['coordinates'],
                    'time': parser.parse(d_data['created_at']).strftime(timeformat) # Allows to filter out by time in Kibana
                }                           # A1-2: Below: Store to es.index
                self.es.index(index='twittmap', doc_type='tweets', id=tweet_id, body=tweet)
                appendlg(self.f, u'{0}: {1}').format(tweet_id, json.dumps(tweet, ensure_ascii=False))
        except Exception as e:
            appendlg(self.f, '{0}: {1}'.format(type(e), str(e)))

    def on_error(self, status): # Return status when disconnects the stream
        print status


if __name__ == '__main__':

    with open('streaming.log', 'a', encoding='utf-8') as f:
        appendlg(f, 'Program starts')

        es = Elasticsearch(hosts=[ep], port=443, use_ssl=True, verify_certs=True, ca_certs=certifi.where())
        l = MyStreamListener(es, f)

        stream = Stream(auth, l)
        stream.filter(track=['Amazon','Food','Google','today','BigData', 'Apple','Samsung','iphone','nyc','dog'])
