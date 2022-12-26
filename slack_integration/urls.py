from django.urls import path

from slack_integration.views.callback import message_callback
from slack_integration.views.channels import default_channel_select
from slack_integration.views.oauth import start_oauth, oauth_callback

app_name = 'slack'
urlpatterns = [
    path('oauth/', start_oauth, name='global_oauth'),
    path('oauth/callback/', oauth_callback, name='global_oauth_callback'),
    path('channel/default/', default_channel_select, name='default_channel_select'),
    path('callback/message/', message_callback, name='message_callback'),
]
