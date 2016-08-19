import base64
from datetime import datetime
import httplib2
import os
import time
import re

from apiclient import discovery
import oauth2client
from oauth2client import client, tools
from twitter.error import TwitterError

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

from tweet import TwitterConnect
import local_settings

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:
            # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
    return credentials


tweet_cache = []


def refresh():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    result = service.users().labels().list(
        userId='me').execute()
    for label in result['labels']:
        if label['name'] == 'chase':
            label_id = label['id']

    result = service.users().messages().list(
        userId='me', labelIds=[label_id]).execute()
    tweet = None
    for message in result['messages']:
        msg = service.users().messages().get(
            userId='me', id=message['id']).execute()
        data = msg['payload']['body']['data']
        s = base64.urlsafe_b64decode(data).decode('utf-8')
        matches = re.search(
            r'A charge of \(\$USD\) ([0-9]+\.[0-9]+) at (.*)(\.\.\.)? '
            r'has been authorized',
            s)
        amount = matches.group(1)
        place = matches.group(2)
        place = re.sub(r'\.\.\.$', '', place)
        tweet = '${} at @{}'.format(amount, place)
        if '$2.49 at @DD/BR' in tweet:
            tweet = '$2.49 at @DunkinDonuts  Damn I probably just picked up my morning coffee.'
        print(tweet)
        break

    tc = TwitterConnect()

    timeline = tc.api.GetUserTimeline(local_settings.TWITTER_USER)
    recent_tweets = []
    for i in range(10):
        status = timeline[i]
        recent_tweets.append(status.text)

    if tweet and (tweet not in recent_tweets) and (tweet not in tweet_cache):
        print('recent tweets')
        print(recent_tweets)
        tweet_cache.append(tweet)
        try:
            tc.tweet(tweet)
        except TwitterError:
            pass


def main():
    while True:
        print(datetime.now())
        refresh()
        time.sleep(60 * 15)


if __name__ == '__main__':
    main()
