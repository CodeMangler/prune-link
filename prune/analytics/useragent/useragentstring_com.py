from prune.utils.url_utils import *
from prune.utils import constants
import django.utils.simplejson as json
from google.appengine.api import memcache
import urllib

__author__ = 'CodeMangler'

class UserAgentParser:
    def __init__(self, ua_string):
        self.ua_string = ua_string
        self.user_agent = None
        self.agent_version = None
        self.language = None
        self.operating_system = None
        self.os_version = None
        self.kernel_version = None
        self.os_variant = None

    def parse(self):
        memcache_key = 'UserAgent_' + self.ua_string

        user_agent_info = memcache.get(memcache_key)
        if not user_agent_info: # Make an API call since we can't find a cached value..
            json_result = fetch_url(constants.USER_AGENT_REQUEST_URL % {"UAS" : urllib.quote(self.ua_string)})
            if json_result:
                user_agent_info = json.loads(json_result)
                memcache.set(memcache_key, user_agent_info) # Cache it

        if user_agent_info:
            self.user_agent = user_agent_info.get('agent_name')
            self.agent_version = user_agent_info.get('agent_version')
            self.language = user_agent_info.get('agent_languageTag')
            self.operating_system = user_agent_info.get('os_type')
            self.os_version = user_agent_info.get('os_versionName')
            self.kernel_version = user_agent_info.get('os_versionNumber')
            self.os_variant = user_agent_info.get('os_name')

            linux_distribution = user_agent_info.get('linux_distribution')
            if linux_distribution and (not linux_distribution.lower() == 'null'):
                self.os_variant = linux_distribution

