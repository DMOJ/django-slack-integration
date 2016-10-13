import requests
from django.core.exceptions import ImproperlyConfigured

from slack_integration.models import SlackIntegration


def list_channels(public=True, private=True, is_member=True):
    result = []
    info = SlackIntegration.get_solo()
    bot = info.bot_name
    token = info.bot_token

    if not token or not bot:
        raise ImproperlyConfigured('Bot user not configured, perform global OAuth')

    if public:
        response = requests.post('https://slack.com/api/channels.list', {
            'token': token, 'exclude_archived': 1
        }).json()
        if response['ok']:
            if is_member:
                result += (chan for chan in response['channels'] if chan['is_member'])
            else:
                result += response['channels']

    if private:
        response = requests.post('https://slack.com/api/groups.list', {
            'token': token, 'exclude_archived': 1
        }).json()
        if response['ok']:
            result += response['groups']

    return result
