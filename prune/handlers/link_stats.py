from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from prune.utils.page_utils import *
from prune.utils.url_utils import *
from prune.models.stats import LinkStats

__author__ = 'CodeMangler'

class LinkStatsHandler(webapp.RequestHandler):
    def get(self):
        self.initialize_members()
        self.response.out.write(render_template("link_stats.html", self.template_parameters))

    def initialize_members(self):
        self.user = users.get_current_user()
        short_url = path(self.request).replace('stats', '').strip('/')
        link_stats = LinkStats.gather_for(short_url)
        self.template_parameters = {
            "user": self.user,
            "link_stats": link_stats,
            "login_url": users.create_login_url(self.request.path),
            "logout_url": users.create_logout_url(self.request.path)
        }

def main():
    application = webapp.WSGIApplication([('/stats/.*', LinkStatsHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
