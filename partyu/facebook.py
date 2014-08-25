# -*- coding: utf-8 -*-

from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
from tornado.log import app_log as log
import json

from keys import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET

class FacebookError(Exception):
    ''' Raised for any error communicating with the API '''
    pass

class FacebookComm(object):

    BASE_URL = 'https://graph.facebook.com/{endpoint}?access_token={app_id}|{app_secret}'\
                    .format(app_id=FACEBOOK_APP_ID, app_secret=FACEBOOK_APP_SECRET, endpoint='{endpoint}')

    SEARCH_ENDPOINT = 'search'
    EVENTS_ENDPOINT = 'events'

    def __init__(self, client):
        self.client = client

    @coroutine
    def get_places(self, ll, q=None):
        url = FacebookComm.BASE_URL.format(endpoint=FacebookComm.SEARCH_ENDPOINT)
        url += '&type=place&center={ll}&distance=100{q}'.format(ll=ll, q='&q='+q if q else '')

        try:
            log.info('Fetching Facebook places from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)
            places = body['data']

        except HTTPError as e:
            raise FacebookError(e.code)

        raise Return(places)

    @coroutine
    def get_page_events(self, page_id):
        url = FacebookComm.BASE_URL.format(endpoint='{page_id}/events'.format(page_id=page_id))

        try:
            log.info('Fetching Facebook events from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)

            events = []
            for e in body['data']:

                if 'attending_count' in e:
                    attending_count = int(e['attending_count'])
                else:
                    attending_count = yield self.get_event_attending_count(e['id'])

                event = {'id': e['id'], 'name': e['name'],
                        'attending': attending_count }

                events.append(event)

        except HTTPError as e:
            raise FacebookError(e.code)

        raise Return(events)

    @coroutine
    def get_event_attending_count(self, event_id):
        url = FacebookComm.BASE_URL.format(endpoint='{event_id}/attending'.format(event_id=event_id))

        try:
            log.info('Fetching Facebook event attending count from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)
            users = body['data']
            attending = len(users)

        except HTTPError as e:
            raise FacebookError(e.code)

        raise Return(attending)