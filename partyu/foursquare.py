# -*- coding: utf-8 -*-

from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
from tornado.log import app_log as log
import json

from keys import FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET

class FoursquareError(Exception):
    ''' Raised for any error communicating with the API '''
    pass

class FoursquareComm(object):

    BASE_URL = 'https://api.foursquare.com/v2/{endpoint}?client_id={client_id}&client_secret={client_secret}'\
                    .format(client_id=FOURSQUARE_CLIENT_ID, client_secret=FOURSQUARE_CLIENT_SECRET, endpoint='{endpoint}')

    VENUES_ENDPOINT = 'venues/search'
    VENUES_CATEGORIES = {'Nightclub': '4bf58dd8d48988d11f941735',
                         'Bar' : '4bf58dd8d48988d116941735',
                         'Brewery': '50327c8591d4c4b30a586d5d',
                         'Lounge' : '4bf58dd8d48988d121941735',
                         'Pub': '4bf58dd8d48988d11b941735',
                         'Other Nightlife': '4bf58dd8d48988d11a941735',
                         'Beach Bar': '52e81612bcbc57f1066b7a0d',
                         'Beer Garden': '4bf58dd8d48988d117941735',
                         'Cocktail Bar': '4bf58dd8d48988d11e941735'}

    def __init__(self, client):
        self.client = client

    @coroutine
    def get_venues(self, ll, radius=10000, limit=30):
        url = FoursquareComm.BASE_URL.format(endpoint=FoursquareComm.VENUES_ENDPOINT)
        url += '&v=20130815&ll={ll}&categoryId={categories}&radius={radius}&limit={limit}&intent=checkin'\
                .format(ll=ll, radius=radius, categories=self._get_categories(), limit=limit)

        try:
            log.info('Fetching Foursquare venues from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FoursquareError(response.code)

            body = json.loads(response.body)

            #Foursquare returns other categories than the ones that I requested
            venues = FoursquareComm.filter_venues(body['response']['venues'])

        except HTTPError as e:
            raise FoursquareError(e.code)

        raise Return(venues)

    def _get_categories(self):
        ''' Return comma-separated list of categories '''
        return ','.join(FoursquareComm.VENUES_CATEGORIES.values())

    @staticmethod
    def filter_venues(venues):
        ''' Return a list of filtered venues '''
        #filter categories
        try:
            valid_venues = [ (v) for v in venues for cat in v['categories'] if cat['id'] in FoursquareComm.VENUES_CATEGORIES.values() ]
        except KeyError as e:
            log.error('Key [{0}] error while filtering categories!', e.message)
            valid_venues = venues
        return valid_venues
