#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import Flask, render_template, request

from aba.aba_parser import ABA_Parser
from networkx.readwrite import json_graph
import json
import jsonpickle
import logging
import time

app = Flask(__name__)

@app.route("/")
def main():
    return render_template("index.html")
    
@app.route("/api", methods=['POST'])
def api():
    logging.basicConfig(filename='main.log',level=logging.DEBUG) 
    
    wall_time_start = time.perf_counter()
    cpu_time_start = time.process_time()

    source_code = request.form['source_code']
    parser = ABA_Parser(source_code)
    parse_errors = parser.parse()
    aba = None
    
    data = dict()
    try:
        aba = parser.construct_aba()
    except Exception as exp:
        data['errors'] = str(exp)
        return json.dumps(data)

    arg_graph = aba.get_combined_argument_graph()
    data['parse_errors'] = parse_errors
    data['arguments'] = json_graph.node_link_data(arg_graph)
    
    data['dispute_trees'] = dict()
    data['dispute_trees_data'] = dict()

    for argument, i in aba.arguments:
        symbol = argument.root
        dispute_tree = aba.get_dispute_tree(symbol, i)
        if dispute_tree is not None:
            for dt_index, dt_graph in enumerate(dispute_tree.graphs):
                dt_name = "%s_%s_%s" % (symbol, i, dt_index)
                data['dispute_trees'][dt_name] = jsonpickle.encode(json_graph.node_link_data(dt_graph), unpicklable=False, max_depth=6, make_refs=False)
                data['dispute_trees_data'][dt_name] = dict()
                data['dispute_trees_data'][dt_name]['is_conflict_free'] = argument.is_conflict_free[i]
                data['dispute_trees_data'][dt_name]['is_stable'] = argument.is_stable[i]
                data['dispute_trees_data'][dt_name]['is_admissible'] = dispute_tree.is_admissible[dt_index]
                data['dispute_trees_data'][dt_name]['is_grounded'] = dispute_tree.is_grounded[dt_index]
                data['dispute_trees_data'][dt_name]['is_ideal'] = dispute_tree.is_ideal[dt_index]
                data['dispute_trees_data'][dt_name]['is_complete'] = dispute_tree.is_complete[dt_index]
    
    wall_time_end = time.perf_counter()
    cpu_time_end = time.process_time()

    wall_time = wall_time_end - wall_time_start
    cpu_time = cpu_time_end - cpu_time_start

    data['statistics'] = dict()
    data['statistics']['wall_time'] = wall_time
    data['statistics']['cpu_time'] = cpu_time
    data['statistics']['symbols'] = len(aba.symbols)
    data['statistics']['assumptions'] = len(aba.assumptions)
    data['statistics']['arguments'] = len(aba.arguments)
    data['statistics']['potential_arguments'] = len(aba.potential_arguments)
    stat = ['is_conflict_free', 'is_stable', 'is_admissible', 'is_grounded', 'is_ideal', 'is_complete']
    for st in stat:
        data['statistics'][st] = len([x for x in data['dispute_trees_data'].values() if x[st]])
    
    return json.dumps(data)

if __name__ == "__main__":
    app.run()
