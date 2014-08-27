# -*- coding: utf-8 -*-
from tornado.gen import coroutine, Return
from operator import itemgetter

class Hotspots(object):

    def __init__(self, comms):
        assert('fsq' in comms and 'fb' in comms)
        self.fsq_comm = comms['fsq']
        self.fb_comm = comms['fb']

    @coroutine
    def get_hotspots(self, ll):
        ''' Return a list of the best hotspots around! '''
        hotspots = []

        #fetch venues around me
        venues = yield self.fsq_comm.get_venues(ll)

        #filter for only those venues that have facebook contact
        fb_venues = { v['contact']['facebook'] : v for v in venues if 'contact' in v and 'facebook' in v['contact'] }
        fb_venue_events = yield self.fb_comm.get_venues_events(fb_venues)

        for vid, venue in fb_venue_events.iteritems():
            for eid, event in venue['events'].iteritems():
                h = Hotspot(venue, event)
                hotspots.append(h.__dict__)

        hotspots = sorted(hotspots, key=itemgetter('score'), reverse=True)
        raise Return(hotspots)

class Hotspot(object):
    def __init__(self, venue, event):
        self.hid = 'e' + event['id'] + ':v' + venue['id']
        self.event = { 'name': event['name'], 'attending': event['attending_count'],
                        'start_time': event['start_time'] }

        self.venue = { 'name': venue['name'],
                        'll': str(venue['location']['lat']) + ',' + str(venue['location']['lng'])}

        self.score = self.calculate_score()

    def calculate_score(self):
        score = self.event['attending_count'] if 'attending_count' in self.event else 0
        return score








