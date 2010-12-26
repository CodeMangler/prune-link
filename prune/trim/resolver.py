from prune.models.db import Link, AggregateLink

__author__ = 'CodeMangler'

class Resolver:

    def __init__(self, request_path):
        self.path = request_path
        self.aggregate = False
        self.resolvable = False
        self.resolution_result = None

    def resolve(self):
        if self.is_empty(self.path):
            return None

        link = Link.find_by_short_url(self.path)
        if link and link.url: # Find a Link that matches
            self.resolvable = True
            self.resolution_result = link.url
        else: # Try finding an AggregateLink
            aggregate_link = AggregateLink.find_by_aggregate_url(self.path)
            if aggregate_link and aggregate_link.url:
                self.aggregate = True
                self.resolvable = True
                self.resolution_result = aggregate_link.url

        return self.resolution_result

    def resolved_url(self):
        return self.resolution_result

    def is_aggregate(self):
        return self.aggregate

    def is_resolvable(self):
        return self.resolvable

    def is_empty(self, text):
        return text is None or text == ''
