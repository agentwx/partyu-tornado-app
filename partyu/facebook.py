# -*- coding: utf-8 -*-

from tornado.gen import coroutine, Return, Task
from tornado.httpclient import HTTPError, HTTPRequest
from tornado.log import app_log as log
from tornado.options import options
import json
import difflib
import datetime
from dateutil import parser

from keys import FACEBOOK_APP_ID, FACEBOOK_APP_SECRET
from utils import friendly_str

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
            request = HTTPRequest(url=url, connect_timeout=options.http_request_timeout, request_timeout=options.http_request_timeout)
            response = yield self.client.fetch(request)

            if response.code != 200:
                raise FacebookError(response.code)

            body = json.loads(response.body)

            places = body['data']
            if len(places) > 0:
                place = places[0]

        except HTTPError as e:
            log.error('Facebook error [{0}] while calling [{1}]!'.format(e, url))
            raise Return(None)

        raise Return(place)

    @coroutine
    def get_unknown_venues_events(self, venues):
        ''' Fetch all events for a list of foursquare venue names '''
        search_url = FacebookComm.BASE_URL.format(endpoint=FacebookComm.SEARCH_ENDPOINT)

        #try matching a foursquare venue to a facebook place
        fb_venues = {}
        tasks = {}

        for vname, venue in venues.iteritems():
            ll = str(venue['location']['lat']) + ',' + str(venue['location']['lng'])
            tasks[vname] = Task(self.get_places, ll=ll, q=friendly_str(vname))

        log.info('Fetching {0} places from Facebook...'.format(len(tasks.keys())))

        places = yield tasks

        for vname, place in places.iteritems():
            if place is None:
                log.info('Venue {0} not found on Facebook!'.format(friendly_str(vname)))
                continue

            venue = venues[vname]
            fb_venues[place['id']] = venue

        if len(fb_venues.keys()) == 0:
            raise Return({})

        # we have the facebook id, fetch the events
        fb_venues_events = yield self.get_venues_events(fb_venues)
        raise Return(fb_venues_events)

    @coroutine
    def get_venues_events(self, venues):
        ''' Fetch all events for all facebook page ids provided '''
        url = FacebookComm.BASE_URL.format(endpoint='events')
        url += '&ids={ids}'.format(ids=','.join(venues.keys()))

        venues_events = {}

        try:
            log.info('Fetching Facebook events from [{0}]'.format(url))
            request = HTTPRequest(url=url, connect_timeout=options.http_request_timeout, request_timeout=options.http_request_timeout)
            response = yield self.client.fetch(request)

        except HTTPError as e:
            log.error('Facebook error [{0}] while calling [{1}]!'.format(e, url))
            raise Return(venues_events)

        body = json.loads(response.body)

        #for every page, fetch its events
        venues_events = {}
        tasks = {}

        for pid, page in body.iteritems():
            if len(page['data']) == 0:
                continue

            events = {}
            attending_fetch_ids = []
            for event in page['data']:
                if self.is_event_expired(event):
                    continue

                if 'attending_count' not in event:
                    attending_fetch_ids.append(event['id'])
                    event['attending_count'] = 0

                events[event['id']] = event

            if len(attending_fetch_ids) > 0:
                tasks[pid] = Task(self.get_event_attending_count, events, attending_fetch_ids)

        log.info('Fetching event attending count for [{0}] venues...'.format(len(tasks.keys())))
        pages_events = yield tasks

        for pid, events in pages_events.iteritems():
            if events is None:
                log.info('No Facebook events for venue [{0}]'.format(venues[pid]['name']))
                continue

            venues_events[pid] = venues[pid]
            venues_events[pid]['events'] = events

        raise Return(venues_events)

    @coroutine
    def get_event_attending_count(self, events, fetch_ids):
        url = FacebookComm.BASE_URL.format(endpoint='attending')
        url += '&ids={ids}'.format(ids=','.join(fetch_ids))

        try:
            log.info('Fetching Facebook event attending count from [{0}]'.format(url))
            request = HTTPRequest(url=url, connect_timeout=options.http_request_timeout, request_timeout=options.http_request_timeout)
            response = yield self.client.fetch(request)

            body = json.loads(response.body)

            for key, value in body.iteritems():
                events[key]['attending_count'] = len(value['data'])

        except HTTPError as e:
            log.error('Facebook error [{0}] while calling [{1}]!'.format(e, url))
            raise Return(events)

        raise Return(events)

    def is_event_expired(self, event):
        edate = parser.parse(event['start_time'])
        tzmaxdate = edate + datetime.timedelta(seconds=60 * 60 * 24)

        #convert date to utc if needed
        if tzmaxdate.utcoffset() is not None:
            maxdate = (tzmaxdate - tzmaxdate.utcoffset()).replace(tzinfo=None)
        else:
            maxdate = tzmaxdate

        if maxdate < datetime.datetime.utcnow():
            log.info('Facebook event [{0}] expired at [{1}]!'.format(event['id'], maxdate))
            return True

        return False
