from google.appengine.api import memcache
from google.appengine.api.users import User
from google.appengine.ext import db
from prune.utils.url_utils import gravatar_picture_url
import re

class Link(db.Model):
    short_url = db.StringProperty()
    url = db.StringProperty() # Not using a LinkProperty sine it expects the values to always be proper Links, which's not quite guaranteed..
    title = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def find_by_short_url(short_url):
        memcache_key = 'Link_' + short_url
        link = memcache.get(memcache_key)
        if not link:
            results = db.GqlQuery('SELECT * FROM Link WHERE short_url = :1', short_url).fetch(1)
            link = results[0] if results else None
            if link:
                memcache.set(memcache_key, link) # Could do db.model_to_protobuff(link), but is it worth it?

        return link

    @staticmethod
    def find_by_url(url):
        memcache_key = 'Link_' + url
        link = memcache.get(memcache_key)
        if not link:
            results = db.GqlQuery('SELECT * FROM Link WHERE url = :1', url).fetch(1)
            link = results[0] if results else None
            if link:
                memcache.set(memcache_key, link) # Could do db.model_to_protobuff(link), but is it worth it?

        return link

class AggregateLink(db.Model):
    aggregate_url = db.StringProperty()
    url = db.StringProperty()
    title = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

    @staticmethod
    def find_by_aggregate_url(aggregate_url):
        memcache_key = 'AggregateLink_' + aggregate_url
        aggregate_link = memcache.get(memcache_key)
        if not aggregate_link:
            results = db.GqlQuery('SELECT * FROM AggregateLink WHERE aggregate_url = :1', aggregate_url).fetch(1)
            aggregate_link = results[0] if results else None
            if aggregate_link:
                memcache.set(memcache_key, aggregate_link) # Could do db.model_to_protobuff(aggregate_link), but is it worth it?

        return aggregate_link

    @staticmethod
    def find_by_url(url):
        memcache_key = 'AggregateLink_URL_' + url
        aggregate_link = memcache.get(memcache_key)
        if not aggregate_link:
            results = db.GqlQuery('SELECT * FROM AggregateLink WHERE url= :1', url).fetch(1)
            aggregate_link = results[0] if results else None
            if aggregate_link:
                memcache.set(memcache_key, aggregate_link) # Could do db.model_to_protobuff(aggregate_link), but is it worth it?

        return aggregate_link

class PrunUser(db.Model):
    # id = db.IntegerProperty() - key().id() is always present and unique, so, no need for an additional field..
    user = db.UserProperty()
    user_id = db.StringProperty()
    user_email = db.StringProperty() # Not using EmailProperty since it doesn't play well with a None (based on the interactive console in the admin app)
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

    def id(self):
        return self.key().id()

    def has_valid_email(self):
        if self.user_email:
            return re.match('.*?@.*?\..*?', self.user_email) is not None
        return False

    @classmethod
    def find_by_id(cls, user_id):
        return PrunUser.get_by_id(user_id)

    @staticmethod
    def find(user):
        memcache_key = "PrunUser_" + str(user)
        prun_user = memcache.get(memcache_key)

        if not prun_user:
            if isinstance(user, User):
                query = db.GqlQuery('SELECT * FROM PrunUser WHERE user = :1', user)
            elif str(user).find('@') != -1:
                query = db.GqlQuery('SELECT * FROM PrunUser WHERE user_email = :1', user)
            else:
                query = db.GqlQuery('SELECT * FROM PrunUser WHERE user_id = :1', user)

            results = query.fetch(1)
            if len(results) != 1: # We expect _exactly_ one user that matches the criteria..
                prun_user = None
            else:
                prun_user = results[0]

            memcache.set(memcache_key, prun_user)

        return prun_user

    @staticmethod
    def create(user):
        prun_user = PrunUser()
        if isinstance(user, User):
            prun_user.user = user
            prun_user.user_email = user.email()
            prun_user.user_id = user.user_id()
        elif str(user).find('@') != -1:
            prun_user.user_email = user
        else:
            prun_user.user_id = user

        prun_user.put()
        return prun_user

    @staticmethod
    def find_or_create(user):
        result = PrunUser.find(user)
        if result is None:
            result = PrunUser.create(user)
        return result

class UserProfile(db.Model):
    prun_user_id = db.IntegerProperty()
    display_name = db.StringProperty(default=None)
    picture_url = db.StringProperty(default=None)
    about = db.StringProperty(multiline=True, default=None)
    websites = db.StringListProperty(default=None)
    twitter = db.StringProperty(default=None)
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

    def uncache(self):
        memcache_key = 'UserProfile_' + str(self.prun_user_id)
        memcache.delete(memcache_key)

    @classmethod
    def find_or_create(cls, prun_user):
        prun_user_id = prun_user.id()
        memcache_key = 'UserProfile_' + str(prun_user_id)
        user_profile = memcache.get(memcache_key)

        if user_profile:
            return user_profile
        else:
            results = db.GqlQuery('SELECT * from UserProfile WHERE prun_user_id = :1', prun_user_id).fetch(1)
            if results:
                user_profile = results[0]
            else:
                user_profile = UserProfile(prun_user_id = prun_user_id)
                if prun_user.has_valid_email():
                    user_profile.picture_url = gravatar_picture_url(prun_user.user_email)
                user_profile.display_name = 'CodeMangler'
                user_profile.about = 'Some random stuff'
                user_profile.websites = ['http://prun.in', 'http://dharampal.name']
                user_profile.twitter = 'CodeMangler'
                user_profile.put()

            memcache.set(memcache_key, user_profile)
            return user_profile

class UserLink(db.Model):
    prun_user_id = db.IntegerProperty()
    short_url = db.StringProperty()
    link_creator = db.BooleanProperty()
    aggregate_url = db.StringProperty() # Redundant information
    url = db.StringProperty() # Redundant information
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

    @classmethod
    def for_user(cls, prun_user, page=0, records_per_page=10):
        return db.GqlQuery('SELECT * FROM UserLink WHERE prun_user_id = :1', prun_user.id()).fetch(limit=records_per_page, offset=(page * records_per_page))

    @staticmethod
    def find_by_url(url, prun_user_id):
        memcache_key = 'UserLink_' + str(prun_user_id) + '_' + url
        user_link = memcache.get(memcache_key)
        if not user_link:
            results = db.GqlQuery('SELECT * FROM UserLink WHERE url= :1 AND prun_user_id = :2', url, prun_user_id).fetch(1)
            user_link = results[0] if results else None
            if user_link:
                memcache.set(memcache_key, user_link) # Could do db.model_to_protobuff(user_link), but is it worth it?

        return user_link

class RequestData(db.Model):
    request_url = db.StringProperty()
    long_url = db.StringProperty()
    short_url = db.StringProperty() # Short/Aggregate URL
    custom_short_url = db.StringProperty()
    request_method = db.StringProperty()
    request_address = db.StringProperty()
    referrer = db.StringProperty()
    raw_headers = db.TextProperty()
    result = db.StringProperty() # Request result -> Created link, Redirected, Error (404/others)
    additional_info = db.TextProperty() # Additional info about the request, if any.. Stack trace for errors etc..
    user = db.UserProperty()
    user_email = db.StringProperty()
    user_id = db.StringProperty()
    processed = db.BooleanProperty(default=False)
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

    def set_user(self, user):
        if user:
            self.user = user
            self.user_email = user.email()
            self.user_id = user.user_id()

# Post processed, stats related entities
class RequestStatistic(): # Base class for all request data statistics
    def increment(self):
        if self.count:
            self.count += 1
        else:
            self.count = 1

    @classmethod
    def find_one(cls, filters):
        query = cls.all() # Expected to call db.Model.all(), since it should only be called on a db.Model

        for filter in filters:
            filter_value = filters[filter]
            if filter_value:
                query.filter(filter + ' =', filter_value)

        results = query.fetch(1)

        if len(results) == 1: # Expecting exactly one match, if present..
            return results[0]
        else:
            return None

    @classmethod
    def create(cls, values):
        result = cls.__new__(cls)
        db.Model.__init__(result, **values) # Ugly, isn't it? Not sure why __new__ can't take care of this automatically..
        return result

    @classmethod
    def find_or_create(cls, values):
        result = cls.find_one(values)
        if result is None:
            result = cls.create(values)
        return result

    @classmethod
    def find_by_short_url(cls, short_url):
        return cls.find_one({'short_url': short_url})

# TODO: Find a way to propagate class variables to remove duplication of short_url and count across all 'RequestStatistic's
class RequestCount(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    count = db.IntegerProperty(default=0)
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

class RequestDate(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    date = db.DateProperty() # App Engine is always 'UTC' btw..
    count = db.IntegerProperty(default=0)
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

class RequestIp(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    count = db.IntegerProperty(default=0)
    ip = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

class RequestReferrer(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    count = db.IntegerProperty(default=0)
    referrer = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

class RequestUserAgentString(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    count = db.IntegerProperty(default=0)
    user_agent_string = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

class RequestUserAgent(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    count = db.IntegerProperty(default=0)
    user_agent = db.StringProperty()
    version = db.StringProperty()
    language = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

class RequestOperatingSystem(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    count = db.IntegerProperty(default=0)
    operating_system = db.StringProperty()
    version = db.StringProperty()
    kernel_version = db.StringProperty()
    variant = db.StringProperty() # Disto/Edition of the OS, if inferrable.. Ubuntu, Fedora, Windows XP, Windows 7 etc..
    language = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)

class RequestLocation(RequestStatistic, db.Model):
    short_url = db.StringProperty() # Short/Aggregate URL
    count = db.IntegerProperty(default=0)
    location = db.GeoPtProperty()
    city = db.StringProperty()
    state = db.StringProperty()
    country = db.StringProperty()
    zip_postal_code = db.StringProperty()
    created_on = db.DateTimeProperty(auto_now_add=True)
    modified_on = db.DateTimeProperty(auto_now=True)
