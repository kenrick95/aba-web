#!/usr/bin/python
# -*- coding: utf-8 -*-
import networkx as nx
import ujson
import logging
import time
from .aba_perf_logger import ABA_Perf_Logger

class ABA_Graph():
    """
    An ABA_Graph object is an argument, i.e. a node, supported by sentences & assumptions
    
    """
        
    def __init__(self, aba = None, root = None):
        self.graphs = []

        self.__history = [[]]
        self.__is_cyclical = [False]

        self.assumptions = [{}]
        self.is_conflict_free = [None]
        self.is_stable = [None]
        
        self.root = root
        self.__aba = aba
        self.__current_index = 0

        self.graphs.append(nx.DiGraph())
        self.__branches = 1

        self.graphs[0].add_node(root)
        self.__history[0].append(root)
        self.__propagate(0, root)
        self.__history[0].pop()

        self.__sort_graphs()

        self.__propagate_assumptions()
        self.__determine_is_conflict_free()

        perf_logger = ABA_Perf_Logger("__determine_is_conflict_free <arg %s>" % root)
        perf_logger.start()
        self.__determine_is_conflict_free()
        perf_logger.end()


        perf_logger = ABA_Perf_Logger("__determine_is_stable <arg %s>" % root)
        perf_logger.start()
        self.__determine_is_stable()
        perf_logger.end()
    
    def __sort_graphs(self):
        graphs_and_is_cyclical = [[x, False] for x in self.graphs]
        for i, item in enumerate(graphs_and_is_cyclical):
            item[1] = self.__is_cyclical[i]

        graphs_and_is_cyclical.sort(key=self.__key_graph_sort)

        self.graphs = [x[0] for x in graphs_and_is_cyclical]
        self.__is_cyclical = [x[1] for x in graphs_and_is_cyclical]

    def __key_graph_sort(self, x):
        return len(x[0].edges())
        
    def __propagate(self, index, node):
        self.__current_index = index
        rules_supporting_node = [x for x in self.__aba.rules if x.result == node]

        # if len(rules_supporting_node) > 1:
        level_graph_copy = self.graphs[index].copy()
        #level_graph_copy = nx.DiGraph(self.graphs[index]) # shallow copy
        level_history_copy = ujson.dumps(self.__history[index])
        level_is_cyclical_copy = ujson.dumps(self.__is_cyclical[index])

        for i, rule in enumerate(rules_supporting_node):
            if i > 0: # "OR" branch, create new argument graph
                self.graphs.append(level_graph_copy.copy())
                #self.graphs.append(nx.DiGraph(level_graph_copy)) # shallow copy
                self.__history.append(ujson.loads(level_history_copy))
                self.__is_cyclical.append(ujson.loads(level_is_cyclical_copy))
                self.assumptions.append({})
                self.is_conflict_free.append(None)
                self.is_stable.append(None)
                self.__current_index += 1
            
            for symbol in rule.symbols:
                self.graphs[self.__current_index].add_edge(node, symbol)
                if symbol is not None:
                    if symbol in self.__history[self.__current_index]:
                        self.__is_cyclical[self.__current_index] = True
                        break
                    self.__history[self.__current_index].append(symbol)
                    self.__propagate(self.__current_index, symbol)
                    self.__history[self.__current_index].pop()
 
    def __propagate_assumptions(self):
        for assumption, symbol in self.__aba.contraries.items():
            for index, graph in enumerate(self.graphs):
                if assumption in graph.nodes():
                    # `assumption` is being attacked by `symbol`
                    self.assumptions[index][assumption] = symbol
    
    def __determine_is_conflict_free(self):
        for index, graph in enumerate(self.graphs):
            conflict_free = True
            for assumption, attacker in self.__aba.contraries.items():
                if attacker in graph.nodes() and assumption in graph.nodes():
                    conflict_free = False
                    break
            self.is_conflict_free[index] = conflict_free
            logging.debug("Argument <%s> index <%d> is conflict free: %s", self.root, index, self.is_conflict_free)

    def __determine_is_stable(self):
        for index, graph in enumerate(self.graphs):
            stable = False
            if self.is_conflict_free[index]:
                stable = True
                for assumption, attacker in self.__aba.contraries.items():
                    if assumption not in graph.nodes():
                        if attacker not in graph.nodes():
                            stable = False
                            break
            
            self.is_stable[index] = stable
            logging.debug("Argument <%s> index <%d> is stable: %s", self.root, index, self.is_stable)

    def __process_is_actual_argument(self, index, node):
        graph = self.graphs[index]
        if self.__is_cyclical[index]:
            return False

        neighbors = graph.successors(node)
        if len(neighbors) == 0: # leaf node
            if node is None or node in self.__aba.assumptions:
                return True
            return False
        
        ret = True
        for neighbor in neighbors:
            ret = ret and self.__process_is_actual_argument(index, neighbor)
        return ret

    def is_actual_argument(self, index = 0):
        return self.__process_is_actual_argument(index, self.root)

    def __str__(self):
        return "Argument '%s'" % self.root
        
    def __repr__(self):
        return str(self)

    
    def __lt__(self, other):
        return len(self.graphs[0].nodes()) < len(other.graphs[0].nodes())
    def __ne__(self, other):
        return self < other or other < self
    def __gt__(self, other):
        return other < self
    def __ge__(self, other):
        return not self < other
    def __le__(self, other):
        return not other < self