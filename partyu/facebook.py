# -*- coding: utf-8 -*-

from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
import json

from keys import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET

class FacebookError(Exception):
    ''' Raised for any error communicating with the API '''
    pass

class FacebookComm(object):

    BASE_URL = 'https://graph.facebook.com/{endpoint}?access_token={app_id}|{app_secret}'\
                    .format(app_id=FACEBOOK_APP_ID, app_secret=FACEBOOK_APP_SECRET, endpoint='{endpoint}')

    SEARCH_ENDPOINT = 'search'

    def __init__(self, client):
        self.client = client

    @coroutine
    def get_places(self, ll):
        url = FacebookComm.BASE_URL.format(endpoint=FacebookComm.SEARCH_ENDPOINT)
        url += '&type=place&center={ll}&distance=100'.format(ll=ll)

        try:
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)

        except HTTPError as e:
            raise FacebookError(e.code)

        raise Return(body)
