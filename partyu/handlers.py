# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
from tornado.gen import coroutine

from hotspots import Hotspots


class GetVenuesHandler(RequestHandler):
    def initialize(self):
        self.fsq_comm = self.application.comms['fsq']

    @coroutine
    def get(self):
        ll = self.get_query_argument('ll', '-30.02,-51.23')
        venues = yield self.fsq_comm.get_venues(ll)
        response = { 'venues': venues }

        self.write(response)


class GetPlacesHandler(RequestHandler):
    def initialize(self):
        self.fb_comm = self.application.comms['fb']

    @coroutine
    def get(self):
        ll = self.get_query_argument('ll', '-30.02,-51.23')
        q = self.get_query_argument('q', None)

        places = yield self.fb_comm.get_places(ll, q)
        self.write({'places': places})


class GetHotspotsHandler(RequestHandler):
    def initialize(self):
        self.comms = self.application.comms

    @coroutine
    def get(self):
        ll = self.get_query_argument('ll', '-30.02,-51.23')

        hotspots = yield Hotspots(self.comms).get_hotspots(ll)

        response = { 'hotspots': hotspots }
        self.write(response)
