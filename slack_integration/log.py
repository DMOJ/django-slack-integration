from django.conf import settings
from django.utils.log import AdminEmailHandler
from django.utils.translation import ugettext

__all__ = ['SlackMessageHandler']


class SlackMessageHandler(AdminEmailHandler):
    def emit(self, record):
        from slack_integration.models import SlackIntegration

        info = SlackIntegration.get_solo()
        if not info.bot_token or not info.error_channel:
            return

        self.__level = record.levelname
        AdminEmailHandler.emit(self, record)

    def send_mail(self, subject, message, *args, **kwargs):
        from slack_integration.api.message import slack_message

        slack_message({
            'text': subject,
            'attachments': [{
                'title': subject,
                'text': message,
                'color': {
                    'ERROR': 'danger',
                    'WARNING': 'warning',
                    'INFO': 'good',
                }.get(self.__level, '#aaa'),
            }],
            'username': getattr(settings, 'SLACK_LOG_ERROR_USERNAME', ugettext('Django Exception')),
        })
