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
        yields = []

        #fetch venues around me
        venues = yield self.fsq_comm.get_venues(ll)

        #filter for only those venues that have facebook contact
        fb_venues = { v['contact']['facebook'] : v for v in venues if 'contact' in v and 'facebook' in v['contact'] }
        future = self.fb_comm.get_venues_events(fb_venues)
        yields.append(future)

        #for the rest, search for the venue on facebook and try to match it to foursquare
        fsq_venues = { v['name'] : v for v in venues if 'contact' not in v or 'facebook' not in v['contact'] }
        future = self.fb_comm.get_unknown_venues_events(fsq_venues)
        yields.append(future)

        #run each fetch in 'parallel' and merge the results
        responses = yield yields
        all_venues_events = { k: v for d in responses for k, v in d.items() }

        #create the hotspot object
        for vid, venue in all_venues_events.iteritems():
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
        score = self.event['attending']
        return score








