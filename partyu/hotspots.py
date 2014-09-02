# -*- coding: utf-8 -*-
from tornado.gen import coroutine, Return

@coroutine
def get_hotspots(comms, ll):
    ''' Return a list of the best hotspots around! '''
    fsq_comm = comms['fsq']
    fb_comm = comms['fb']

    hotspots = []
    tasks = []

    #fetch venues around me from foursquare
    venues = yield fsq_comm.get_venues(ll)

    #filter for only those venues that have facebook contact
    fb_venues = { v['contact']['facebook'] : v for v in venues if 'contact' in v and 'facebook' in v['contact'] }
    future = fb_comm.get_venues_events(fb_venues)
    tasks.append(future)

    #for the rest, search for the venue on facebook and try to match it to foursquare
    fsq_venues = { v['name'] : v for v in venues if 'contact' not in v or 'facebook' not in v['contact'] }
    future = fb_comm.get_unknown_venues_events(fsq_venues)
    tasks.append(future)

    #run each fetch in 'parallel' and merge the results
    responses = yield tasks
    all_venues_events = { k: v for d in responses for k, v in d.items() }

    #create the hotspot object
    for vid, venue in all_venues_events.iteritems():
        events = venue['events'] if 'events' in venue else {}
        h = Hotspot(vid, venue, events)
        hotspots.append(h.__dict__)

    raise Return(hotspots)

class Hotspot(object):
    def __init__(self, hid, venue, events):
        self.hid = hid

        self.events = [ {'id': eid, 'name': event['name'], 'attending': event['attending_count'], 'start_time': event['start_time'] }
                            for eid, event in events.iteritems() ]

        self.venue = { 'name': venue['name'],
                        'll': str(venue['location']['lat']) + ',' + str(venue['location']['lng']) }
