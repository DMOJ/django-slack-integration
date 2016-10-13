def slack_message(message, channel=None):
    global slack_message
    from slack_integration.api.message import slack_message
    return slack_message(message, channel)
