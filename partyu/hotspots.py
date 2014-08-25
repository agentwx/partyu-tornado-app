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

        #for each venue that has facebook id, fetch its events
        fb_venues = [ v for v in venues if 'contact' in v and 'facebook' in v['contact'] ]
        for venue in fb_venues:
            events = yield self.fb_comm.get_page_events(venue['contact']['facebook'])

            for event_id, event in events.iteritems():
                h = Hotspot(eid=event_id, vname=venue['contact']['facebookName'], ename=event['name'],
                            ll=str(venue['location']['lat']) + ',' + str(venue['location']['lng']))

                h.score = Hotspot.calculate_score(event, venue)
                hotspots.append(h.__dict__)

        hotspots = sorted(hotspots, key=itemgetter('score'), reverse=True)
        raise Return(hotspots)

class Hotspot(object):
    def __init__(self, eid, ll, ename, vname):
        self.event_id = eid
        self.ll = ll
        self.ename = ename
        self.vname = vname
        self.score = 0

    @staticmethod
    def calculate_score(event, venue):
        score = event['attending']

        if 'hereNow' in venue:
            score += venue['hereNow']['count']

        return score








