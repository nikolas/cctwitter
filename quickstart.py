from __future__ import unicode_literals

import httplib2
import os
import time
import re

from apiclient import discovery
import oauth2client
from oauth2client import client, tools

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


def refresh():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = 5
    result = service.users().messages().list(
        userId='me', maxResults=results).execute()
    for m in range(results):
        msgid = result['messages'][m]['id']
        msgresult = service.users().messages().get(
            userId='me', id=msgid).execute()

        date = None
        subject = None
        snippet = msgresult['snippet']
        for header in msgresult['payload']['headers']:
            if header['name'] == 'From':
                sender = header['value']
            elif header['name'] == 'Subject':
                subject = header['value']
            elif header['name'] == 'Date':
                date = header['value']

        if re.match(r'card', sender, re.I):
            print(date)
            print(sender)
            print(subject)
            print(snippet)
            print()
            break

    tc = TwitterConnect()
    timeline = tc.api.GetUserTimeline(local_settings.TWITTER_USER)
    recent_tweets = []
    for i in range(10):
        recent_tweets.append(timeline[i].text)

    if snippet not in recent_tweets:
        print(snippet)
        # tc.tweet(snippet)


def main():
    while True:
        refresh()
        time.sleep(60 * 5)


if __name__ == '__main__':
    main()
