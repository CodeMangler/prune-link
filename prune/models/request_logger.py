from db import RequestData

__author__ = 'CodeMangler'

class RequestLogger:
    def __init__(self, request_url, request_headers, request_address, referrer, user=None):
        self.request_data = RequestData(request_url = request_url, raw_headers = request_headers, request_address = request_address, referrer = referrer)
        self.request_data.set_user(user)

    def log(self, short_url, request_result, additional_info = None):
        if not self.request_data:
            return

        self.request_data.short_url = short_url
        self.request_data.result = request_result
        self.request_data.additional_info = additional_info

        self.request_data.put()

    def data(self):
        return self.request_data

