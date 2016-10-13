from __future__ import unicode_literals

from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class SlackIntegration(SingletonModel):
    team_id = models.CharField(max_length=20, blank=True, verbose_name=_('slack team id'))
    team_name = models.CharField(max_length=100, blank=True, verbose_name=_('slack team name'))
    access_token = models.CharField(max_length=100, blank=True, verbose_name=_('slack access token'))
    bot_name = models.CharField(max_length=30, blank=True, verbose_name=_('slack bot id'))
    bot_token = models.CharField(max_length=100, blank=True, verbose_name=_('slack bot token'))
    error_channel = models.CharField(max_length=20, blank=True, verbose_name=_('slack error channel'),
                                     help_text=_('The channel where Django error posts go, and also acts '
                                                 'as the default channel.'))
