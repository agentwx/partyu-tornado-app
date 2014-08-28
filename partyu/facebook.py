# -*- coding: utf-8 -*-

from tornado.gen import coroutine, Return
from tornado.httpclient import HTTPError
from tornado.log import app_log as log
import json
import difflib

from keys import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from utils import friendly_str

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
    def get_places(self, ll, q):
        url = FacebookComm.BASE_URL.format(endpoint=FacebookComm.SEARCH_ENDPOINT)
        place = None

        try:
            url += '&type=place&center={ll}&distance=100&q={q}'.format(ll=ll, q=q)

            log.info('Fetching Facebook places from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)

            places = body['data']
            if len(places) > 0:
                place = places[0]

        except HTTPError as e:
            raise FacebookError(e.code)

        raise Return(place)

    @coroutine
    def get_unknown_venues_events(self, venues):
        fb_venues = {}

        #try matching a foursquare venue to a facebook place
        for vname, venue in venues.iteritems():
            vname = friendly_str(vname)
            fb_place = yield self.get_places(q=vname, ll=str(venue['location']['lat']) + ',' + str(venue['location']['lng']))
            if fb_place is None:
                log.info('Venue {0} not found on Facebook!'.format(vname))
                continue

            fb_venues[fb_place['id']] = venue
            '''
            fb_place['name'] = friendly_str(fb_place['name'])
            if len(difflib.get_close_matches(vname, [fb_place['name']])) > 0:
                fb_venues[fb_place['id']] = venue
            else:
                log.info('Venue [{0}] not close enough to [{1}], ignoring!'.format(vname, fb_place['name']))
                continue'''

        if len(fb_venues.keys()) == 0:
            raise Return({})

        fb_venues_events = yield self.get_venues_events(fb_venues)
        raise Return(fb_venues_events)

    @coroutine
    def get_venues_events(self, venues):
        url = FacebookComm.BASE_URL.format(endpoint='events')
        url += '&ids={ids}'.format(ids=','.join(venues.keys()))

        try:
            log.info('Fetching Facebook events from [{0}]'.format(url))
            response = yield self.client.fetch(url)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)

            #for every page, fetch its events
            venues_events = {}
            for pid, page in body.iteritems():
                if len(page['data']) == 0:
                    continue

                events = {}
                attending_fetch_ids = []
                for event in page['data']:
                    if 'attending_count' not in event:
                        attending_fetch_ids.append(event['id'])
                        event['attending_count'] = 0

                    events[event['id']] = event

                if len(attending_fetch_ids) > 0:
                    yield self.get_event_attending_count(events, attending_fetch_ids)

                venues_events[pid] = venues[pid]
                venues_events[pid]['events'] = events

        except HTTPError as e:
            raise FacebookError(e.code)

        raise Return(venues_events)

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
                events[key]['attending_count'] = len(value['data'])

        except HTTPError as e:
            raise FacebookError(e.code)
