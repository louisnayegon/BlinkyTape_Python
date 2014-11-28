#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path

import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from twitter_tags import twitter_tags

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", tornado.web.RedirectHandler, {"url": r"/tags"}),
            (r"/tags", MainHandler),
            (r"/tags/edit", EditHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=True,
            autoescape=None
            )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(
            "index.html",
            twitter_tags=twitter_tags
        )
        self.set_status(200)


class EditHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            tag = self.get_argument('tag')
            self.render(
                "edit.html",
                twitter_tags=twitter_tags,
                tag=tag
            )
            self.set_status(200)
        # will do some searching
        except AssertionError:
            self.write("no params")

    def post(self):
        tag = self.get_argument('tag')
        import pdb; pdb.set_trace()
        twitter_tags[tag]['red'] = self.get_argument('red')
        twitter_tags[tag]['green'] = self.get_argument('green')
        twitter_tags[tag]['blue'] = self.get_argument('blue')
        self.redirect("/tags", status=303)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
