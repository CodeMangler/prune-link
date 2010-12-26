from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from prune.models.db import Link
from prune.utils.url_utils import fetch_title

__author__ = 'CodeMangler'

# Updates Link Title
class LinkInfoWorker(webapp.RequestHandler):
    def post(self):
        short_url = self.request.get('short_url')
        link = Link.find_by_short_url(short_url)
        if link:
            if link.title:
                return # nothing to be done if title is already populated
            else:
                title = self.get_title(link.url)
                if title:
                    link.title = title
                    link.put()
                    memcache.delete('Link_' + short_url) # To ensure that the next find on Link fetches the updated entry from the datastore

    def get_title(self, url):
        memcache_key = 'LinkInfo_' + url
        title = memcache.get(memcache_key)
        if not title:
            title = fetch_title(url)
            memcache.set(memcache_key, title)
        return title

def main():
    application = webapp.WSGIApplication([('/task/linkinfo', LinkInfoWorker)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
