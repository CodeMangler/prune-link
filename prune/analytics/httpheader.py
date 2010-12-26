__author__ = 'CodeMangler'

class HeaderParser:
    def __init__(self, headers):
        self.raw_headers = self.as_dictionary(headers)

    def as_dictionary(self, headers):
        if isinstance(headers, dict):
            return headers
        elif isinstance(headers, basestring):
            result = {}
            entries = headers.strip('{}').split('\',')
            for entry in entries:
                keyvalue = entry.split('\':')
                if len(keyvalue) == 2:
                    result[keyvalue[0].strip('\' ')] = keyvalue[1].strip('\' ')
            return result
        else:
            return {}

    def headers(self):
        return self.raw_headers
