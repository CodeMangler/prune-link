from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import users
from prune.utils.page_utils import *
from prune.utils.url_utils import *
from prune.models.db import PrunUser
from prune.models.db import UserProfile

__author__ = 'CodeMangler'

class EditProfileHandler(webapp.RequestHandler):
    def get(self):
        self.user = users.get_current_user()
        if not self.user:
            self.redirect('/') # Redirect back to the home page. No point showing an error page for ths.
            return
        self.initialize_fields(self.user)
        self.response.out.write(render_template("edit_profile.html", self.template_parameters))

    def post(self):
        self.user = users.get_current_user()
        if not self.user:
            show_error_page(self, 400, 'You have to be logged-in to edit your profile.')

        self.initialize_fields(self.user)
        display_name = self.request.get('display-name')
        about = self.request.get('about')
        twitter = self.request.get('twitter')
        websites = self.request.get('websites')

        self.user_profile.display_name = display_name
        self.user_profile.about = about
        self.user_profile.twitter = twitter
        self.user_profile.websites = [website.strip() for website in re.split('\n\r|\r\n|\n|\r', websites)] if websites else None
        self.user_profile.put()

        self.user_profile.uncache()

        self.redirect('/profile') # Done updating, take back to show the updated profile

    def initialize_fields(self, user):
        self.prun_user = PrunUser.find_or_create(user)
        self.user_profile = UserProfile.find_or_create(self.prun_user)
        websites_list = "\n".join([site for site in self.user_profile.websites if site]) if self.user_profile.websites else ''
        self.template_parameters = {
            "user": user,
            "user_profile": self.user_profile,
            "websites_list": websites_list,
            "login_url": users.create_login_url(self.request.path),
            "logout_url": users.create_logout_url(self.request.path)
        }

def main():
    application = webapp.WSGIApplication([('/profile/.*', EditProfileHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
