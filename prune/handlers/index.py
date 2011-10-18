from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from prune.utils.page_utils import render_template
from prune.utils.page_utils import show_error_page
from prune.utils.url_utils import *
from prune.trim.resolver import Resolver
from prune.trim.trimmer import Trimmer
from prune.models.request_logger import RequestLogger
from prune.utils.utils import *
from prune.utils.constants import RequestResult

import os

__author__ = 'CodeMangler'

class IndexHandler(webapp.RequestHandler):
    def get(self):
        request_path = path(self.request)
        self.initialize_members('GET')

        if is_valid_url(request_path):
            self.shorten(request_path, None, self.user)
        else:
            self.resolve(request_path, self.user)

    def post(self):
        long_url = self.request.get('long-url')
        custom_short_url = self.request.get('custom-short-url')
        self.initialize_members('POST')
        self.shorten(long_url, custom_short_url, self.user) # Accept everything.. Is filtering out bad URLs any good?

    def initialize_members(self, request_method):
        self.user = users.get_current_user()
        self.logger = RequestLogger(self.request.url, request_method, str(self.request.headers), self.request.remote_addr, os.getenv('HTTP_REFERER'), self.user)
        self.template_parameters = {
            "user": self.user,
            "login_url": users.create_login_url(self.request.path),
            "logout_url": users.create_logout_url(self.request.path)
        }

    def shorten(self, url_to_shorten, custom_short_url, user):
        short_url = Trimmer(url_to_shorten).shorten(custom_short_url, user)
        self.template_parameters["short_url"] = short_url

        if short_url != custom_short_url:
            self.template_parameters["custom_short_url_error_message"] = 'The selected custom short URL already exists, and hece we\'ve generated a new short URL'

        self.logger.log(url_to_shorten, custom_short_url, short_url, RequestResult.NEW_SHORT_URL_CREATED)
        taskqueue.add(url='/task/linkinfo', params={'short_url': short_url}) # Update Link Info

        self.response.out.write(render_template("index.html", self.template_parameters))

    def resolve(self, request_path, user):
        if is_empty(request_path):
            self.response.out.write(render_template("index.html", self.template_parameters))
            return

        resolver = self.resolver_for(request_path)
        if resolver.is_resolvable():
            if resolver.is_aggregate():
                resolved_url =  '/stats/' + request_path # Display aggregate stats?
            else:
                # No logging for aggregate url requests since they resolve to their stats.. Logging them would pollute stats..
                resolved_url = resolver.resolved_url()
                self.logger.log(resolved_url, None, request_path, RequestResult.SHORT_URL_RESOLVED)
                taskqueue.add(url='/task/stats', params={'request_data_key': self.logger.data().key()}) # Update Stats

            self.redirect(resolved_url)
        else:
            self.logger.log(None, None, None, RequestResult.ERROR, '404: /%(PATH)s not found' % {"PATH" : request_path})
            show_error_page(self, 404, "The requested page was not found")
            return

    def resolver_for(self, request_path):
        resolver_memcache_key = 'Resolver_' + request_path
        resolver = memcache.get(resolver_memcache_key)
        if not resolver:
            resolver = Resolver(request_path)
            resolver.resolve()
            memcache.set(resolver_memcache_key, resolver)

        return resolver

def main():
    application = webapp.WSGIApplication([('/.*', IndexHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
