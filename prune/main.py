#!/usr/bin/env python

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

from prune.handlers.index import IndexHandler
from prune.handlers.profile import ProfileHandler
from prune.handlers.stats import StatsHandler
from prune.tasks.linkinfo import LinkInfoWorker
from prune.tasks.stats import StatsWorker


def main():
    application = webapp.WSGIApplication([('/stats/.*', StatsHandler), ('/profile/.*', ProfileHandler),
                                          ('/task/linkinfo', LinkInfoWorker), ('/task/stats', StatsWorker),
                                          ('/.*', IndexHandler)],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
