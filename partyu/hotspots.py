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
        #venues = [ v for v in venues if 'contact' in v and 'facebook' in v['contact'] ]

        #list all facebook venue ids so we can fetch them all at once
        venues_fb_ids = [ v['contact']['facebook'] for v in venues if 'contact' in v and 'facebook' in v['contact'] ]

        events = yield self.fb_comm.get_pages_events(venues_fb_ids)

        for event_id, event in events.iteritems():
            h = Hotspot(eid=event_id, vname=event['venue_id'], ename=event['name'],
                        location=event['location'])

            h.score = Hotspot.calculate_score(event)
            hotspots.append(h.__dict__)

        hotspots = sorted(hotspots, key=itemgetter('score'), reverse=True)
        raise Return(hotspots)

class Hotspot(object):
    def __init__(self, eid, location, ename, vname):
        self.event_id = eid
        self.location = location
        self.ename = ename
        self.vname = vname
        self.score = 0

    @staticmethod
    def calculate_score(event):
        score = event['attending']
        return score








