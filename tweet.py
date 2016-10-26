import twitter
from twitter.error import TwitterError
import local_settings


class TwitterConnect:
    def __init__(self):
        self.api = twitter.Api(
            consumer_key=local_settings.CONSUMER_KEY,
            consumer_secret=local_settings.CONSUMER_SECRET,
            access_token_key=local_settings.ACCESS_TOKEN_KEY,
            access_token_secret=local_settings.ACCESS_TOKEN_SECRET)

    def tweet(self, s):
        print('Tweeting: {}'.format(s))
        try:
            self.api.PostUpdate(s)
        except TwitterError:
            pass
