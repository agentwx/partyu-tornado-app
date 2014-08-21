# -*- coding: utf-8 -*-
from tornado.web import RequestHandler
from tornado.gen import coroutine, Return


class GetVenuesHandler(RequestHandler):
    def initialize(self):
        self.comm = self.application.comms['4sq']

    @coroutine
    def get(self):
        ll = self.get_query_argument('ll')

        venues = yield self.comm.get_venues(ll)

        response = { 'venues': venues }

        self.write(response)
