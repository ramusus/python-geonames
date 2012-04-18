import httplib
import simplejson
import sys
import logging
from urllib import urlencode

from responsehandlers.element_tree import ElementTreeResponseHandler
from responsehandlers.json import JsonResponseHandler

# Default GeoNames server to connect to.
DEFAULT_GEONAMES_SERVER = 'api.geonames.org'
DEFAULT_RESPONSE_HANDLER = ElementTreeResponseHandler

class GeoNames():
    """
    Accessor class for the online GeoNames geographical database.
    """
    def __init__(self, server=DEFAULT_GEONAMES_SERVER, default_handler=DEFAULT_RESPONSE_HANDLER):
        """
        Create a GeoNames object.
        """
        self.server = server
        self.response_handler = default_handler()

    def _api_call(self, method, resource, **kwargs):
        """
        Makes a generic API call to geonames webservice.
        """
        if not kwargs.get('username'):
            kwargs['username'] = 'demo'
        uri = "/%s?%s" %(resource, urlencode(kwargs))
        c = self.get_connection()
        c.request(method, uri)
        response = c.getresponse()
        if not 200 == response.status:
            raise GeoNameException("Expected a 200 reponse but got %s." %(response.status))
        data = response.read()

        logging.debug(uri)
        logging.debug(data)

        return self.response_handler.get_processed_data(data)

    def get_connection(self):
        """
        Return a connection object to the webservice.
        """
        c = httplib.HTTPConnection(self.server)
        return c

    # TODO: move this to a helper object.lat=55.90167&lng=37.4375&username=demo&lang=ru
    def search(self, name, country):
        """
        Perform a search for a country's information.
        """
        # we only want exact matches, and we only want one possible match.
        return self._api_call('GET', 'search', name_equals=name, country=country, maxRows=1)

    def find_nearby_wikipedia(self, **kwargs):
        '''
        Perform a search for finding nearby Wikipedia Entries / reverse geocoding
        This service comes in two flavors. You can either pass the lat/long or a postalcode/placename.
        Full documentation http://www.geonames.org/export/wikipedia-webservice.html
        '''
        try:
            assert kwargs.get('lat') and kwargs.get('lng') or kwargs.get('postalcode')
        except:
            raise ValueError('You need to either pass lat, long or a postalcode')

        if isinstance(self.response_handler, JsonResponseHandler):
            resource = 'findNearbyWikipediaJSON'
        elif False:
            resource = 'findNearbyWikipediaRSS'
        elif isinstance(self.response_handler, ElementTreeResponseHandler):
            resource = 'findNearbyWikipedia'
        else:
            raise TypeError('Unexpected response_handler for request of this type')

        return self._api_call('GET', resource, **kwargs)

class GeoNameException(Exception):
    """
    Error initializing GeoNames accessor.
    """
    pass