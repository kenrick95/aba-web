from flask import Flask, render_template, request

from aba.aba_parser import ABA_Parser
from networkx.readwrite import json_graph
import json
import jsonpickle
import logging

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")
    
@app.route("/api", methods=['POST'])
def api():
    # logging.basicConfig(filename='main.log',level=logging.DEBUG) 
    
    source_code =request.form['source_code']
    parser = ABA_Parser(source_code)
    parse_errors = parser.parse()
    
    aba = parser.construct_aba()
    
    arg_graph = aba.get_combined_argument_graph()
    data = dict()
    data['parse_errors'] = parse_errors
    data['arguments'] = json_graph.node_link_data(arg_graph)
    
    data['dispute_trees'] = dict()
    data['dispute_trees_data'] = dict()
    for symbol in aba.symbols:
       data['dispute_trees'][symbol] = jsonpickle.encode(json_graph.node_link_data(aba.get_dispute_tree(symbol).graph), unpicklable = False, max_depth = 6, make_refs = False)
       data['dispute_trees_data'][symbol] = dict()
       data['dispute_trees_data'][symbol]['is_conflict_free'] = aba.get_argument(symbol).is_conflict_free()
       data['dispute_trees_data'][symbol]['is_admissible'] = aba.get_dispute_tree(symbol).is_admissible
       data['dispute_trees_data'][symbol]['is_grounded'] = aba.get_dispute_tree(symbol).is_grounded
    
    return json.dumps(data)

if __name__ == "__main__":
    app.run()
