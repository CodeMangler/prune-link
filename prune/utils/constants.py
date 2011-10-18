__author__ = 'CodeMangler'

USER_AGENT_REQUEST_URL = 'http://www.useragentstring.com/?uas=%(UAS)s&getJSON=all'
GEOLOCATION_REQUEST_URL = 'http://api.ipinfodb.com/v2/ip_query.php?key=0bde88d75043de5ab285b843b0a682cf8a50687e21e3a39d2e82cba582456509&ip=%(IP)s&output=json&timezone=false'
SHORT_LINK_LENGTH = 6 # Sufficient for 44261653680 (62P6) URLs. If we run out, we can simply increase this, provided we haven't placed any constraints on the DB field.
AGGREGATE_LINK_LENGTH = 8

class RequestResult:
    NEW_SHORT_URL_CREATED = 'Created'
    SHORT_URL_RESOLVED = 'Resolved'
    ERROR = 'Error'
