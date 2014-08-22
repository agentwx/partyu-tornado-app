# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
from tornado.gen import coroutine


class GetVenuesHandler(RequestHandler):
    def initialize(self):
        self.fsq_comm = self.application.comms['fsq']
        self.fb_comm = self.application.comms['fb']

    @coroutine
    def get(self):
        ll = self.get_query_argument('ll')
        #venues = yield self.fsq_comm.get_venues(ll)
        #response = { 'venues': venues }

        places = yield self.fb_comm.get_places(ll)
        response = { 'places': places }
        self.write(response)
