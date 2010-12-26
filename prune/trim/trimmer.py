import random
from string import join
from prune.models.db import *
from prune.utils import constants

__author__ = 'CodeMangler'

class Trimmer:
    VALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def __init__(self, url_to_trim):
        self.url = url_to_trim

    def shorten(self, user=None):
        user_link = None
        prun_user = None

        if user:
            prun_user = PrunUser.find_or_create(user)

        # If the user is logged in, check if he already has a short url for this url. If so, show the same one.. Otherwise, create new..
        existing_user_link = None
        if prun_user:
            existing_user_link = UserLink.find_by_url(self.url, prun_user.id())

        if not existing_user_link: # Nothing found, so create new..
            short_url = ''
            while True:
                short_url = self.generate_random_sequence(constants.SHORT_LINK_LENGTH)
                existing_short_link = Link.find_by_short_url(short_url) # If the short link is taken, loop back and generate another..
                if not existing_short_link:
                    break

            link = Link(url = self.url, short_url = short_url)
            link.put()
            # Associate link with the current user if logged in..
            if prun_user:
                user_link = UserLink(prun_user_id = prun_user.id(), short_url = short_url, url = self.url)
        else:
            user_link = existing_user_link
            short_url = user_link.short_url

        # Create or find an aggregate link and associate that with the URL
        link_creator = False
        aggregate_link = AggregateLink.find_by_url(self.url)
        if not aggregate_link: # If no existing aggregate URL found, create one..
            aggregate_url = ''
            while True:
                aggregate_url = self.generate_random_sequence(constants.AGGREGATE_LINK_LENGTH)
                existing_aggregate_link = AggregateLink.find_by_aggregate_url(aggregate_url) # If the link is already taken, loop back and generate another..
                if not existing_aggregate_link:
                    break

            aggregate_link = AggregateLink(url = self.url, aggregate_url = aggregate_url)
            aggregate_link.put()
            link_creator = True
        else:
            aggregate_url = aggregate_link.aggregate_url

        # Commit user links.. (Create/Update) - Associate the link with the user..
        if user_link:
            user_link.link_creator = link_creator
            user_link.aggregate_url = aggregate_url
            user_link.put()

        return short_url

    def generate_random_sequence(self, length):
        random_id = []
        for i in range(0, length):
            random_id.append(random.choice(self.VALID_CHARS))
        return join(random_id, '')
