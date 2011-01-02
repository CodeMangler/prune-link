from prune.models.db import *

__author__ = 'CodeMangler'

def filter_value(list_of_values, value):
    return [x for x in list_of_values if x != value]

def gather_stats(prun_user):
    user_links = UserLink.for_user(prun_user)
    return filter_value([LinkStats.gather_for(user_link.short_url) for user_link in user_links], None)

class LinkStats:
    short_url = None # Short/Aggregate URL..
    aggregate_url = None
    url = ''
    title = ''
    is_aggregate = False
    click_count = 0
    total_click_count = 0
    clicks = {} # Timestamp vs Count
    referrers = {} # Referrer vs Count
    browsers = {}
    operating_systems = {}
    countries = {} # Country vs Count
    cities = {}
    is_valid = False

    def __init__(self, short_url):
        self.short_url = short_url
        link = Link.find_by_short_url(short_url)
        if link:
            self.url = link.url
            self.title = link.title
            self.is_aggregate = False
            self.aggregate_url = AggregateLink.find_by_url(self.url).aggregate_url
            self.is_valid = True
        else:
            aggregate_link = AggregateLink.find_by_aggregate_url(short_url)
            if aggregate_link:
                self.url = aggregate_link.url
                self.title = self.find_title(self.url)
                self.is_aggregate = True
                self.aggregate_url = short_url
                self.is_valid = True
            else: # Just being explicit..
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
        request_referrers = RequestReferrer.find_by_short_url(self.short_url)
        if request_referrers:
            for request_referrer in request_referrers:
                self.referrers[request_referrer.referrer] = request_referrer.count
        # TODO: Further analysis? Like, identify popular sources: EMail, Twitter, Facebook, Desktop Clients, Mobile Clients etc..?

    def gather_browser_stats(self):
        request_user_agents = RequestUserAgent.find_by_short_url(self.short_url)
        if request_user_agents:
            for request_user_agent in request_user_agents:
                browser = request_user_agent.user_agent
                if not self.browsers.has_key(browser):
                    self.browsers[browser] = 0 # Add key if it doesn't exist
                self.browsers[browser] += request_user_agent.count

    def gather_os_stats(self):
        request_operating_systems = RequestOperatingSystem.find_by_short_url(self.short_url)
        if request_operating_systems:
            for request_operating_system in request_operating_systems:
                os = request_operating_system.operating_system
                if not self.operating_systems.has_key(os):
                    self.operating_systems[os] = 0 # Add key if it doesn't exist
                self.operating_systems[os] += request_operating_system.count

    def gather_location_stats(self):
        request_locations = RequestLocation.find_by_short_url(self.short_url)
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
