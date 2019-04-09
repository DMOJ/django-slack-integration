import json
from copy import copy

import requests
from django.utils import six
from django.core.exceptions import ImproperlyConfigured

from slack_integration.exceptions import SlackAPIError
from slack_integration.models import SlackIntegration


def slack_message(message, channel=None):
    info = SlackIntegration.get_solo()
    if not info.bot_token:
        raise ImproperlyConfigured('Bot has not been configured, perform global OAuth')

    if isinstance(message, dict):
        message = copy(message)
    elif isinstance(message, list):
        message = {'attachments': message}
    elif isinstance(message, six.string_types):
        message = {'text': message}
    else:
        raise TypeError('Unsupported message type')

    if channel is None:
        if not info.error_channel:
            raise ImproperlyConfigured('No default channel configured')
        message['channel'] = info.error_channel
    else:
        message['channel'] = channel

    if 'attachments' in message:
        message['attachments'] = json.dumps(message['attachments'])

    message['token'] = info.bot_token

    response = requests.post('https://slack.com/api/chat.postMessage', message).json()
    if not response['ok']:
        raise SlackAPIError(response['error'])
    return response['message']
