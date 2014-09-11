# -*- coding: utf-8 -*-
import tornado.ioloop
from tornado.web import Application
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options
import motor

from handlers import GetVenuesHandler, GetPlacesHandler, GetHotspotsHandler
from foursquare import FoursquareComm
from facebook import FacebookComm


class PartyuApp(Application):
    def __init__(self, *args, **kwargs):
        super(PartyuApp, self).__init__(*args, **kwargs)

        #setup MongoDB
        db_client = motor.MotorClient(options.mongodb_uri)
        self.db = db_client[options.mongodb_database]

        #setup http client
        AsyncHTTPClient.configure(None, max_clients=options.http_max_clients)
        self.client = AsyncHTTPClient()

        #setup comm classes
        self.comms = {}
        self.comms['fsq'] = FoursquareComm(self.client)
        self.comms['fb'] = FacebookComm(self.client)


def main():
    define('host', default='127.0.0.1', help='Host IP')
    define('port', default=8080, help='Port')
    define('mongodb_uri', default='mongodb://admin:EC9vMARWLckz@partyu-seekermob.rhcloud.com:27017', help='MongoDB URI')
    define('mongodb_database', default='partyu', help='MongoDB database')
    define('http_max_clients', default=1000, help='AsyncHTTP max clients')
    define('http_request_timeout', default=20.0, help='Timeout for all HTTP requests')
    tornado.options.parse_command_line()

    application = PartyuApp([(r"/getvenues", GetVenuesHandler),
                             (r"/getplaces", GetPlacesHandler),
                             (r"/gethotspots", GetHotspotsHandler),])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

