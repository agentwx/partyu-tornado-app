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
    def get_pages_events(self, page_ids):
        url = FacebookComm.BASE_URL.format(endpoint='events')
        url += '&ids={ids}'.format(ids=','.join(page_ids))

        try:
            log.info('Fetching Facebook events from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)

            events = {}
            attending_fetch_ids = []

            for page_id, page in body.iteritems():
                for e in page['data']:

                    if 'attending_count' in e:
                        attending_count = int(e['attending_count'])
                    else:
                        attending_count = 0
                        attending_fetch_ids.append(e['id'])

                    event = { 'name': e['name'], 'attending': attending_count, 'venue_id': page_id, 'location': e['location'] }

                    events[e['id']] = event

            #fetch attending count for all events at once
            if len(attending_fetch_ids) > 0:
                yield self.get_event_attending_count(events, attending_fetch_ids)

        except HTTPError as e:
            raise FacebookError(e.code)

        raise Return(events)

    @coroutine
    def get_event_attending_count(self, events, fetch_ids):
        url = FacebookComm.BASE_URL.format(endpoint='attending')
        url += '&ids={ids}'.format(ids=','.join(fetch_ids))

        try:
            log.info('Fetching Facebook event attending count from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)

            for key, value in body.iteritems():
                events[key]['attending'] = len(value['data'])

        except HTTPError as e:
            raise FacebookError(e.code)
