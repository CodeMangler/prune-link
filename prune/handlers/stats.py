from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from prune.models.stats import *
from prune.utils.page_utils import *

__author__ = 'CodeMangler'

class StatsHandler(webapp.RequestHandler):
    def get(self):
        self.user = users.get_current_user()
        if not self.user:
            #show_error_page(self, 400, 'You have to be logged-in to view your link statistics.')
            self.redirect(users.create_login_url(self.request.path))
            return

        self.initialize_members(self.user)
        self.response.out.write(render_template("stats.html", self.template_parameters))

    def initialize_members(self, user):
        self.prun_user = PrunUser.find_or_create(user)
        self.user_link_stats = gather_stats(self.prun_user)
        self.template_parameters = {
            "user": user,
            "user_link_stats": self.user_link_stats,
            "login_url": users.create_login_url(self.request.path),
            "logout_url": users.create_logout_url('/')
        }

def main():
    application = webapp.WSGIApplication([('/stats.*', StatsHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
