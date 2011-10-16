from prune.models.db import *
from prune.analytics.referrer import *

__author__ = 'CodeMangler'

def filter_value(list_of_values, value):
    return [x for x in list_of_values if x != value]

def gather_stats(prun_user):
    user_links = UserLink.all_for_user(prun_user)
    return filter_value([LinkStats.gather_for(user_link.short_url) for user_link in user_links], None)

class LinkStats:
    def __init__(self, short_url):
        self.initialize_fields()

        self.short_url = short_url
        link = Link.find_by_short_url(short_url)
        if link:
            self.url = link.url
            self.title = link.title
            self.creation_date = link.created_on
            self.is_aggregate = False
            self.aggregate_url = AggregateLink.find_by_url(self.url).aggregate_url
            self.is_valid = True
        else:
            aggregate_link = AggregateLink.find_by_aggregate_url(short_url)
            if aggregate_link:
                self.url = aggregate_link.url
                self.creation_date = aggregate_link.created_on
                self.title = self.find_title(self.url)
                self.is_aggregate = True
                self.aggregate_url = short_url
                self.is_valid = True
            else: # Just being explicit..
                self.is_valid = False

    def initialize_fields(self):
        self.short_url = None # Short/Aggregate URL..
        self.aggregate_url = None
        self.url = ''
        self.title = ''
        self.creation_date = None
        self.is_aggregate = False
        self.click_count = 0
        self.total_click_count = 0
        self.clicks = {} # Timestamp vs Count
        self.referrers = {} # Referrer vs Count
        self.browsers = {}
        self.operating_systems = {}
        self.countries = {} # Country vs Count
        self.cities = {}
        self.is_valid = False

    def find_title(self, url):
        link = Link.find_by_url(url)
        if link:
            return link.title
        return ''

    @classmethod
    def gather_for(cls, short_url):
        link_stats = LinkStats(short_url)
        if link_stats.is_valid:
            link_stats.gather_click_stats()
            link_stats.gather_referrer_stats()
            link_stats.gather_browser_stats()
            link_stats.gather_os_stats()
            link_stats.gather_location_stats()
            return link_stats
        else:
            return None

    def gather_click_stats(self):
        request_count = RequestCount.find_one_by_short_url(self.short_url)
        if request_count:
            self.click_count = request_count.count

        if not self.is_aggregate:
            aggregate_count = RequestCount.find_one_by_short_url(self.aggregate_url)
            if aggregate_count:
                self.total_click_count = aggregate_count.count
        else:
            self.total_click_count = self.click_count

        request_dates = RequestDate.find_by_short_url(self.short_url, order_by=['date'])
        if request_dates:
            for request_date in request_dates:
                self.clicks[request_date.date] = request_date.count

    def gather_referrer_stats(self):
        request_referrers = RequestReferrer.find_by_short_url(self.short_url, order_by=['date'])
        if request_referrers:
            for request_referrer in request_referrers:
                referrer = self.referrers[request_referrer.date] if self.referrers.has_key(request_referrer.date) else ReferrerStat(request_referrer.date)

                if request_referrer.referrer == ReferrerTypes.GOOGLE:
                    referrer.google += request_referrer.count
                elif request_referrer.referrer == ReferrerTypes.BING:
                    referrer.bing += request_referrer.count
                elif request_referrer.referrer == ReferrerTypes.YAHOO:
                    referrer.yahoo += request_referrer.count
                elif request_referrer.referrer == ReferrerTypes.TWITTER:
                    referrer.twitter += request_referrer.count
                elif request_referrer.referrer == ReferrerTypes.FACEBOOK:
                    referrer.facebook += request_referrer.count
                elif request_referrer.referrer == ReferrerTypes.DIRECT:
                    referrer.direct += request_referrer.count
                else:
                    referrer.other += request_referrer.count

                self.referrers[request_referrer.date] = referrer

    def gather_browser_stats(self):
        request_user_agents = RequestUserAgent.find_by_short_url(self.short_url, order_by=['date'])
        if request_user_agents:
            for request_user_agent in request_user_agents:
                browser = request_user_agent.user_agent
                if not self.browsers.has_key(browser):
                    self.browsers[browser] = 0 # Add key if it doesn't exist
                self.browsers[browser] += request_user_agent.count

    def gather_os_stats(self):
        request_operating_systems = RequestOperatingSystem.find_by_short_url(self.short_url, order_by=['date'])
        if request_operating_systems:
            for request_operating_system in request_operating_systems:
                os = request_operating_system.operating_system
                if not self.operating_systems.has_key(os):
                    self.operating_systems[os] = 0 # Add key if it doesn't exist
                self.operating_systems[os] += request_operating_system.count

    def gather_location_stats(self):
        request_locations = RequestLocation.find_by_short_url(self.short_url, order_by=['date'])
        if request_locations:
            for request_location in request_locations:
                city = request_location.city
                country = request_location.country
                city_country = city + ', ' + country

                if not self.cities.has_key(city_country):
                    self.cities[city_country] = 0 # Add key if it doesn't exist
                if not self.countries.has_key(country):
                    self.countries[country] = 0 # Add key if it doesn't exist

                self.cities[city_country] += request_location.count
                self.countries[country] += request_location.count

class ReferrerStat:
    def __init__(self, date):
        self.direct = 0
        self.google = 0
        self.bing = 0
        self.yahoo = 0
        self.twitter = 0
        self.facebook = 0
        self.other = 0
        self.date = date
