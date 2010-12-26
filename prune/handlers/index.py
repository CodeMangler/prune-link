from google.appengine.api import taskqueue
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from prune.utils.template_utils import render_template
from prune.utils.url_utils import *
from prune.trim.resolver import Resolver
from prune.trim.trimmer import Trimmer
from prune.models.request_logger import RequestLogger
from prune.utils.constants import RequestResult

import os

__author__ = 'CodeMangler'

class IndexHandler(webapp.RequestHandler):
    def get(self):
        # Get the requested path
        # If the path is empty, show empty home page
        # If the path is a URL itself, create a new short link (home page with expanded link populated) (and the aggregate link and everything else..)
        # If the path is a short link id, fetch the expanded URL and redirect (301/302?) to it (or show stats if it's an aggregate)
        # If all else fails, show the error page
        request_path = path(self.request)
        user = users.get_current_user()

        logger = RequestLogger(self.request.url, str(self.request.headers), self.request.remote_addr, os.getenv('HTTP_REFERER'), user)

        template_parameters = {
            "user" : user,
            "login_url" : users.create_login_url(self.request.path),
            "logout_url" : users.create_logout_url(self.request.path)
        }

        resolver = self.resolver_for(request_path)
        if resolver.is_resolvable():
            if resolver.is_aggregate():
                resolved_url =  '/stats/' + request_path # Display aggregate stats?
            else:
                # No logging for aggregate url requests since they resolve to their stats.. Logging them would pollute stats..
                resolved_url = resolver.resolved_url()
                logger.log(request_path, RequestResult.SHORT_URL_RESOLVED)
                taskqueue.add(url='/task/stats', params={'request_data_key': logger.data().key()}) # Update Stats

            self.redirect(resolved_url)
        elif self.is_empty(request_path):
            self.response.out.write(render_template("index.html", template_parameters))
        elif is_valid_url(request_path):
            short_url = Trimmer(request_path).shorten(user)
            template_parameters["short_url"] = short_url
            logger.log(short_url, RequestResult.NEW_SHORT_URL_CREATED)
            taskqueue.add(url='/task/linkinfo', params={'short_url': short_url}) # Update Link Info

            self.response.out.write(render_template("index.html", template_parameters))
        else:
            logger.log(None, RequestResult.ERROR, '404: /{path} not found'.format(**{"path": request_path}))
            self.error(404) # Send a HTTP Not Found
            self.response.out.write(render_template("error.html", {"message" : "The requested page was not found"}))

    def resolver_for(self, request_path):
        resolver_memcache_key = 'Resolver_' + request_path
        resolver = memcache.get(resolver_memcache_key)
        if not resolver:
            resolver = Resolver(request_path)
            resolver.resolve()
            memcache.set(resolver_memcache_key, resolver)

        return resolver

    def is_empty(self, text):
        return text is None or text == ''

def main():
    application = webapp.WSGIApplication([('/.*', IndexHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
