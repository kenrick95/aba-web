import tornado.wsgi
import wsgiref.simple_server
import main

application = main.make_app()
wsgi_app = tornado.wsgi.WSGIAdapter(application)
if __name__ == '__main__':
    server = wsgiref.simple_server.make_server('', 8888, wsgi_app)
    server.serve_forever()