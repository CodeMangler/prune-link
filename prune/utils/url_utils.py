import urllib
import urlparse
import re
from google.appengine.api import urlfetch

__author__ = 'CodeMangler'

def is_valid_url(url):
    """ The URL must have at least the hostname (netloc) for it to be valid. The rest (scheme, path...) are allowed to be missing. """
    result = urlparse.urlparse(url)
    return (result.netloc is not None) and (result.netloc != '')

def path(request):
    return urllib.unquote(request.path.lstrip('/')).decode('utf8')

def fetch_url(url):
    response = urlfetch.fetch(url)
    if response.status_code == 200:
         return response.content
    return None

def fetch_title(url):
    page = fetch_url(url)
    if page:
        match = re.search('.*?<\s*?title\s*?>(.*?)</\s*?title\s*>', page, re.DOTALL | re.IGNORECASE)
        if match and len(match.groups()) != 0:
            return match.groups()[0]
    return None
