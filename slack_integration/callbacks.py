import six

from datetime import datetime

from django.core.urlresolvers import reverse_lazy

from slack_integration.exceptions import InvalidSlackCallbackError

_registry = {}

callback_url = reverse_lazy('slack:message_callback')


class SlackCallbackMeta(type):
    def __call__(cls, data):
        self = super(SlackCallbackMeta, cls).__call__(data)

        for name, value in self.actions:
            self.process(name, value)
        return self.message


@six.add_metaclass(SlackCallbackMeta)
class SlackCallbackHandler(object):

    def __init__(self, data):
        try:
            self.response_url = data['response_url']
            self.user = data['user']['id']
            self.username = data['user']['name']
            self.channel = data['channel']['name']
            self.channel_id = data['channel']['id']
            self.team = data['team']['domain']
            self.team_id = data['team']['id']
            self.action_ts = data['action_ts']
            self.message_ts = data['message_ts']
            self.actions = [(act['name'], act['value']) for act in data['actions']]
            self.message = data['original_message']
            self.attachment_id = data['attachment_id']
        except (ValueError, KeyError, TypeError) as e:
            __import__('traceback').print_exc()
            raise InvalidSlackCallbackError(e.message)

        try:
            self.action_time = datetime.utcfromtimestamp(float(self.action_ts))
            self.message_time = datetime.utcfromtimestamp(float(self.action_ts))
        except ValueError as e:
            raise InvalidSlackCallbackError(e.message)

    def process(self, name, value):
        raise NotImplementedError()


def slack_callback(name):
    def decorator(handler):
        def unregister():
            del _registry[name]

        if name in _registry:
            raise ValueError('Already registered: %s' % name)

        handler.callback_id = name
        handler.unregister = unregister
        _registry[name] = handler
        return handler

    return decorator


def unregister_callback(item):
    if isinstance(item, six.string_types):
        del _registry[item]
    elif hasattr(item, 'callback_id'):
        del _registry[item.callback_id]
    else:
        raise TypeError("Don't know how to unregister")


def get_handler(name):
    return _registry.get(name)
