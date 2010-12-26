from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

__author__ = 'CodeMangler'

class ProfileHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Hello world!')

def main():
    application = webapp.WSGIApplication([('/profile/.*', ProfileHandler)], debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
