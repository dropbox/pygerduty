class Error(Exception):
    pass


class IntegrationAPIError(Error):
    def __init__(self, message, event_type):
        self.event_type = event_type
        self.message = message

    def __str__(self):
        return "Creating {0} event failed: {1}".format(self.event_type,
                                                       self.message)


class BadRequest(Error):
    def __init__(self, payload, *args, **kwargs):
        # Error Responses don't always contain all fields.
        # Sane defaults must be set.
        self.code = payload.get("error", {}).get('code', 99999)
        self.errors = payload.get("error", {}).get('errors', [])
        self.message = payload.get("error", {}).get('message', str(payload))

        Error.__init__(self, *args)

    def __str__(self):
        return "{0} ({1}): {2}".format(
            self.message, self.code, self.errors)


class NotFound(Error):
    pass
