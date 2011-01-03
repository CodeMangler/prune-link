import urlparse
import re
from prune.utils.utils import *

__author__ = 'CodeMangler'

class ReferrerAnalyzer:
    @classmethod
    def referrer_type(cls, referrer_url):
        if is_empty(referrer_url):
            return ReferrerTypes.DIRECT

        parse_result = urlparse.urlparse(referrer_url)
        referrer_host = parse_result.netloc if parse_result.netloc else ''

        if is_empty(referrer_host):
            return ReferrerTypes.DIRECT

        for referrer_type in ReferrerTypes.REFERRER_HOST_MATCHER:
            if ReferrerTypes.REFERRER_HOST_MATCHER[referrer_type].match(referrer_host):
                return referrer_type

        return ReferrerTypes.OTHER

class ReferrerTypes:
    DIRECT = 'Direct'
    GOOGLE = 'Google'
    BING = 'Bing'
    YAHOO = 'Yahoo!'
    TWITTER = 'Twitter'
    FACEBOOK = 'Facebook'
    OTHER = 'Other'

    REFERRER_HOST_MATCHER = {
        GOOGLE: re.compile('google\..{2,6}', re.IGNORECASE|re.DOTALL),
        BING: re.compile('bing\..{2,6}', re.IGNORECASE|re.DOTALL),
        YAHOO: re.compile('yahoo\..{2,6}', re.IGNORECASE|re.DOTALL),
        TWITTER: re.compile('twitter\..{2,6}', re.IGNORECASE|re.DOTALL),
        FACEBOOK: re.compile('facebook\..{2,6}', re.IGNORECASE|re.DOTALL)
    }
