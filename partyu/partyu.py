# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

from handlers import GetVenuesHandler
from foursquare import FoursquareComm


class PartyuApp(Application):
    def __init__(self, *args, **kwargs):
        super(PartyuApp, self).__init__(*args, **kwargs)

        self.db = None

        self.client = AsyncHTTPClient()

        self.comms = {}
        self.comms['4sq'] = FoursquareComm(self.client)
        self.comms['fb'] = None


def main():
    define("host", default="127.0.0.1", help="Host IP")
    define("port", default=8080, help="Port")
    tornado.options.parse_command_line()

    application = PartyuApp([(r"/getvenues", GetVenuesHandler),])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

