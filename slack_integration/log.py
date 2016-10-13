from django.utils.log import AdminEmailHandler
from django.utils.translation import ugettext

__all__ = ['SlackMessageHandler']


class SlackMessageHandler(AdminEmailHandler):
    def emit(self, record):
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
            'username': ugettext('Django Exception'),
        })
