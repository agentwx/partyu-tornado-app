# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application
from tornado.httpclient import AsyncHTTPClient

from handlers import GetVenuesHandler
from foursquare import FoursquareComm


class PartyuApp(Application):
    def __init__(self, *args, **kwargs):
        super(PartyuApp, self).__init__(*args, **kwargs)

        #init MongoDB
        self.db = None

        #init http client
        self.client = AsyncHTTPClient()

        #init api comms
        self.comms = {}
        self.comms['4sq'] = FoursquareComm(self.client)
        self.comms['fb'] = None


def main(address):
    application = PartyuApp([(r"/getvenues", GetVenuesHandler),])

    application.listen(8080, address)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    address = "127.0.0.1"
    main(address)
