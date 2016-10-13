class SlackAPIError(Exception):
    def __init__(self, code):
        super(SlackAPIError, self).__init__(code)
        self.code = code


class InvalidSlackCallbackError(Exception):
    pass
