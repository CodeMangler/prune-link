from prune.utils.url_utils import *
from prune.utils import constants
import django.utils.simplejson as json
from google.appengine.api import memcache

__author__ = 'CodeMangler'

class GeoLocator:
    def __init__(self, ip):
        self.ip = ip
        self.latitude = None
        self.longitude = None
        self.city = None
        self.state = None
        self.country = None
        self.zip_postal_code = None

    def locate(self):
        memcache_key = 'GeoLocation_' + self.ip

        geo_location = memcache.get(memcache_key)
        if not geo_location: # Call the API if we can't find a cached value..
            json_result = fetch_url(constants.GEOLOCATION_REQUEST_URL.format(self.ip))
            if json_result:
                geo_location = json.loads(json_result)
                memcache.set(memcache_key, geo_location) # Cache it

        if geo_location:
            self.latitude = geo_location.get('Latitude')
            self.longitude = geo_location.get('Longitude')
            self.city = geo_location.get('City')
            self.state = geo_location.get('RegionName')
            self.country = geo_location.get('CountryName')
            self.zip_postal_code = geo_location.get('ZipPostalCode')

