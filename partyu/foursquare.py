# -*- coding: utf-8 -*-

from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
import json

from keys import FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET

class FoursquareError(Exception):
    ''' Raised for any error communicating with the API '''
    pass

class FoursquareComm(object):

    BASE_URL = 'https://api.foursquare.com/v2/{method}?client_id={client_id}&client_secret={client_secret}'\
                    .format(client_id=FOURSQUARE_CLIENT_ID, client_secret=FOURSQUARE_CLIENT_SECRET, method='{method}')

    VENUES_SEARCH = 'venues/search'

    def __init__(self, client):
        self.client = client

    @coroutine
    def get_venues(self, ll):
        url = FoursquareComm.BASE_URL.format(method=FoursquareComm.VENUES_SEARCH)
        url += '&v=20130815&ll={ll}&categoryId=4d4b7105d754a06376d81259'.format(ll=ll)

        try:
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FoursquareError(response.code)

            body = json.loads(response.body)
            venues = body['response']['venues']

        except HTTPError as e:
            raise FoursquareError(e.code)

        raise Return(venues)
