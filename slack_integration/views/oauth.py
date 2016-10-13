from binascii import hexlify
from urllib import urlencode

import os
import requests
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import redirect

from slack_integration.models import SlackIntegration

STATE_KEY = 'slack_oauth_global_state'


def start_oauth(request):
    if not hasattr(settings, 'SLACK_API_CLIENT_ID'):
        raise ImproperlyConfigured('Attempt to use Slack OAuth without SLACK_API_CLIENT_ID in settings.py')
    if not hasattr(settings, 'SLACK_API_CLIENT_SECRET'):
        raise ImproperlyConfigured('Attempt to use Slack OAuth without SLACK_API_CLIENT_SECRET in settings.py')

    params = {'client_id': settings.SLACK_API_CLIENT_ID, 'scope': 'bot',
              'redirect_uri': request.build_absolute_uri(reverse('slack:global_oauth_callback'))}

    state = hexlify(os.urandom(16))
    cache.set(STATE_KEY, state)
    if cache.get(STATE_KEY) == state:
        params['state'] = state

    return redirect('https://slack.com/oauth/authorize?' + urlencode(params))


def oauth_callback(request):
    if request.GET.get('state') != cache.get(STATE_KEY):
        return HttpResponseBadRequest('Invalid state')

    code = request.GET.get('code')
    if not code:
        return HttpResponseBadRequest('Invalid code')

    result = requests.post('https://slack.com/api/oauth.access', {
        'client_id': settings.SLACK_API_CLIENT_ID,
        'client_secret': settings.SLACK_API_CLIENT_SECRET,
        'code': code,
        'redirect_uri': request.build_absolute_uri(request.path)
    }).json()

    store = SlackIntegration.get_solo()
    try:
        store.team_id = result['team_id']
        store.team_name = result['team_name']
        store.access_token = result['access_token']
        store.bot_name = result['bot']['bot_user_id']
        store.bot_token = result['bot']['bot_access_token']
    except KeyError:
        return HttpResponseBadRequest('Slack OAuth returned bad results:\n%s' % store, content_type='text/plain')
    else:
        store.save()

    return HttpResponse('Authentication success', content_type='text/plain')
