import tornado.ioloop
import tornado.web


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("views/index.html")

def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()