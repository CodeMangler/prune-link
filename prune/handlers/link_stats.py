from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from prune.models.db import PrunUser

__author__ = 'CodeMangler'

class LinkStatsHandler(webapp.RequestHandler):
    def get(self):
        self.initialize_members()
        self.response.out.write('View link stats')

    def initialize_members(self):
        self.user = users.get_current_user()
        self.template_parameters = {
            "user": self.user,
            "user-id": PrunUser.find_or_create(self.user).key().id() if self.user else None,
            "login_url": users.create_login_url(self.request.path),
            "logout_url": users.create_logout_url(self.request.path)
        }

def main():
    application = webapp.WSGIApplication([('/stats/.*', LinkStatsHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
