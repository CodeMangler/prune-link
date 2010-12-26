from google.appengine.api.datastore_types import GeoPt
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from prune.models.db import Link
from prune.models.db import AggregateLink
from prune.models.db import RequestData
from prune.models.db import RequestCount
from prune.models.db import RequestDate
from prune.models.db import RequestIp
from prune.models.db import RequestReferrer
from prune.models.db import RequestUserAgentString
from prune.models.db import RequestUserAgent
from prune.models.db import RequestOperatingSystem
from prune.models.db import RequestLocation
from prune.analytics.httpheader import HeaderParser
from prune.analytics.useragent.useragentstring_com import UserAgentParser
from prune.analytics.geolocation.iponfodb import GeoLocator

__author__ = 'CodeMangler'

class StatsWorker(webapp.RequestHandler):
    def post(self):
        request_data_key = self.request.get('request_data_key')
        request_data = RequestData.get(request_data_key)
        if request_data:
            parser = HeaderParser(request_data.raw_headers)
            raw_headers = parser.headers()

            short_url = request_data.short_url
            self.update_stats(short_url, request_data, raw_headers)

            # TODO: Too many DataStore calls? Denormalize?
            # Update stats for the Aggregate Link
            link = Link.find_by_short_url(short_url)
            if link:
                resolved_url = link.url
                aggregate_link = AggregateLink.find_by_url(resolved_url)
                if aggregate_link:
                    aggregate_url = aggregate_link.aggregate_url
                    self.update_stats(aggregate_url, request_data, raw_headers)

            request_data.processed = True # Mark the request data as processed, so that we can maybe delete it later..
            request_data.put()

    def update_stats(self, short_url, request_data, raw_headers):
        self.update_request_count(short_url)
        self.update_request_ip(short_url, request_data)
        self.update_referrer(short_url, request_data, raw_headers)
        self.update_user_agent(short_url, raw_headers)
        self.update_location(short_url, request_data)

    def update_request_count(self, short_url):
        request_count = RequestCount.find_or_create({'short_url': short_url})
        request_count.increment()
        request_count.put()

        request_date =  RequestDate.find_or_create({'short_url': short_url, 'date': db.DateProperty().now()}) # NOTE: App Engine uses 'UTC' Dates (and times)..
        request_date.increment()
        request_date.put()

    def update_referrer(self, short_url, request_data, headers):
        if not request_data.referrer:
            request_data.referrer = headers.get('Referer') # .get(...) instead of [...] to avoid KeyError
            request_data.put()

        if request_data.referrer:
            request_referrer = RequestReferrer.find_or_create({'short_url': short_url, 'referrer': request_data.referrer})
            request_referrer.increment()
            request_referrer.put()

    def update_request_ip(self, short_url, request_data):
        request_ip = RequestIp.find_or_create({'short_url': short_url, 'ip': request_data.request_address})
        request_ip.increment()
        request_ip.put()

    def update_user_agent(self, short_url, raw_headers):
        user_agent_string = raw_headers.get('User-Agent') # .get(...) instead of [...] to avoid KeyError

        if user_agent_string:
            # Store Request User Agent String
            request_user_agent_string = RequestUserAgentString.find_or_create({'short_url': short_url, 'user_agent_string': user_agent_string})
            request_user_agent_string.increment()
            request_user_agent_string.put()

            # Explode user-agent string into user-agent and OS (external service)?
            parser = UserAgentParser(user_agent_string)
            parser.parse()

            user_agent = parser.user_agent
            agent_version = parser.agent_version
            language = parser.language
            operating_system = parser.operating_system
            os_version = parser.os_version
            kernel_version = parser.kernel_version
            os_variant = parser.os_variant

            # Store actual user agent and OS and update their counts
            request_user_agent = RequestUserAgent.find_or_create({'short_url': short_url, 'user_agent': user_agent, 'version': agent_version, 'language': language})
            request_user_agent.increment()
            request_user_agent.put()

            request_operating_system = RequestOperatingSystem.find_or_create({'short_url': short_url, 'operating_system': operating_system,
                                                                              'version': os_version, 'kernel_version': kernel_version,
                                                                              'variant': os_variant, 'language': language})
            request_operating_system.increment()
            request_operating_system.put()

    def update_location(self, short_url, request_data):
        locator = GeoLocator(request_data.request_address)
        locator.locate()

        latitude = locator.latitude
        longitude = locator.longitude
        if latitude and longitude:
            location = GeoPt(latitude, longitude)
            request_location = RequestLocation.find_or_create({'short_url': short_url, 'location': location,
                                                               'city': locator.city, 'state': locator.state,
                                                               'country': locator.country, 'zip_postal_code': locator.zip_postal_code})
            request_location.increment()
            request_location.put()

def main():
    application = webapp.WSGIApplication([('/task/stats', StatsWorker)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
