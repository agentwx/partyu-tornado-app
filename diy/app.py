# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.gen import coroutine, Return

from keys import FOURSQUARE_CLIENT_ID, FOURSQUARE_CLIENT_SECRET

FOURSQUARE_BASE_URL = 'https://api.foursquare.com/v2/venues/search?client_id={client_id}&client_secret={client_secret}'

class MainHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.client = AsyncHTTPClient()

    @coroutine
    def get(self):
        ll = self.get_query_argument('ll')

        venues = yield self.get_fq_venues(ll)

        self.write(venues)

    @coroutine
    def get_fq_venues(self, ll):
        url = FOURSQUARE_BASE_URL.format(client_id=FOURSQUARE_CLIENT_ID, client_secret=FOURSQUARE_CLIENT_SECRET)
        url += '&v=20130815&ll={ll}&categoryId=4d4b7105d754a06376d81259'.format(ll=ll)

        response = yield self.client.fetch(url)
        raise Return(response.body)

application = tornado.web.Application([
    (r"/", MainHandler),
])

def main(address):
    application.listen(8080, address)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    address = "127.0.0.1"
    main(address)
