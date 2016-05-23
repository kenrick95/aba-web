import tornado.ioloop
import tornado.web
from aba.aba_parser import ABA_Parser
import networkx as nx
from networkx.readwrite import json_graph
import json

class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.render("views/index.html")


class ApiHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def post(self):
        source_code = self.get_argument('source_code')
        parser = ABA_Parser(source_code)
        parse_result = parser.parse()
        aba = parser.construct_aba()
        
        graph = aba.get_combined_argument_graph()
        data = json_graph.node_link_data(graph)
        
        self.write(json.dumps(data))
        self.flush()
        self.finish()

def make_app():
    return tornado.web.Application([
        (r"/", IndexHandler),
        (r"/api/?", ApiHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()