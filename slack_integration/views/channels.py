from django import forms
from django.shortcuts import render
from django.utils.translation import gettext

from slack_integration.api.channels import list_channels
from slack_integration.models import SlackIntegration


class ChannelSelectForm(forms.Form):
    channel = forms.ChoiceField()

    def __init__(self, *args, **kwargs):
        super(ChannelSelectForm, self).__init__(*args, **kwargs)
        self.fields['channel'].choices = [(channel['id'], ('#' if 'is_channel' in channel else '') + channel['name'])
                                          for channel in list_channels(is_member=True)]


def default_channel_select(request):
    if request.method == 'POST':
        form = ChannelSelectForm(request.POST)
        if form.is_valid():
            SlackIntegration.objects.update(error_channel=form.cleaned_data['channel'])
    else:
        form = ChannelSelectForm(initial={'channel': SlackIntegration.get_solo().error_channel})

    return render(request, 'slack/channel_select.html', {
        'title': gettext('Select Default Channel'),
        'form': form,
    })
