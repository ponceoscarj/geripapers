import tweepy
import time
import config

# authentication
auth = tweepy.OAuthHandler(config.api_key, config.api_key_secret)
auth.set_access_token(config.access_token, config.access_token_secret)
api = tweepy.API(auth)


class Listener(tweepy.Stream):
    def on_status(self, status):
        """
        We initiate Listener and run on_status to handle tweets root-level attributes

        Once Listener(tweepy.Stream) is set up and finds tweets with specific keywords (hashtags)
        which will be set up below, it will ignore those tweets that has
        the following attributes: "retweeted_status" (retweet) and "quoted_status" (quoted tweet),
        and those tweets from a specific user (@geripapers).
        This Listener is set to tweet those tweets that do not meet any of the aforementioned characteristics.
        """
        if hasattr(status, "retweeted_status"):
            print('A retweet')
            return
        if hasattr(status, "quoted_status"):
            print('A quoted tweet')
            return
        if status.user.id == api.verify_credentials()._json['id']:
            print('Own tweet')
        else:
            print(f'{status.user.id} - {status.user.screen_name}: {status.text}')
            api.retweet(status.id)
        time.sleep(0.2)


if __name__ == '__main__':
    # Setting up the Listener with own twitter API authentication details
    stream_tweet = Listener(config.api_key, config.api_key_secret, config.access_token, config.access_token_secret)
    # Setting up keywords to be searched by the twitter streaming
    keywords = ['#geripapers', '#geripaper', '#geritwitter', '#gerijc']
    # Initiate twitter streaming
    stream_tweet.filter(track=keywords)
