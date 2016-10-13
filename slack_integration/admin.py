from django.contrib import admin
from solo.admin import SingletonModelAdmin

from slack_integration.models import SlackIntegration


class SlackIntegrationAdmin(SingletonModelAdmin):
    exclude = ()

admin.site.register(SlackIntegration, SlackIntegrationAdmin)
