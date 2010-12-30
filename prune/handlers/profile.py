from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from prune.utils.page_utils import *
from prune.utils.url_utils import *
from prune.models.db import PrunUser
from prune.models.db import UserProfile

__author__ = 'CodeMangler'

class ProfileHandler(webapp.RequestHandler):
    def get(self):
        self.user = users.get_current_user()
        self.prun_user = None

        request_path = path(self.request).lower().replace('profile', '').strip('/')
        if not self.is_empty(request_path):
            self.prun_user = PrunUser.find_by_id(long(request_path))
            if not self.prun_user:
                show_error_page(self, 404, 'No such user')
                return
        elif self.user: # If no user id provided, show currently logged-in user's profile
            self.prun_user = PrunUser.find_or_create(self.user)
        else:
            self.redirect('/') # Redirect back to the home page. No point showing an error page for ths.
            return

        self.user_profile = UserProfile.find_or_create(self.prun_user)

        self.template_parameters = {
            "user": self.user,
            "user_profile": self.user_profile,
            "login_url": users.create_login_url(self.request.path),
            "logout_url": users.create_logout_url(self.request.path)
        }

        self.response.out.write(render_template("profile.html", self.template_parameters))

    def is_empty(self, text):
        return text is None or text == ''

def main():
    application = webapp.WSGIApplication([('/profile.*', ProfileHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
