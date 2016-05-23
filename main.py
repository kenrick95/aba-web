from flask import Flask, render_template, request

from aba.aba_parser import ABA_Parser
from networkx.readwrite import json_graph
import json

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")
    
@app.route("/api", methods=['POST'])
def api():
    source_code =request.form['source_code']
    parser = ABA_Parser(source_code)
    parse_result = parser.parse()
    aba = parser.construct_aba()
    
    graph = aba.get_combined_argument_graph()
    data = json_graph.node_link_data(graph)
    
    return json.dumps(data)

if __name__ == "__main__":
    app.run()
