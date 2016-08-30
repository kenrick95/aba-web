#!/usr/bin/python
# -*- coding: utf-8 -*-
import networkx as nx
import pickle, ujson
from .aba_constants import *
import logging

class ABA_Dispute_Tree():
    """
    ABA_Dispute_Tree
    
    Vertices: <argument + label>
    Edges: attacks
    
    """
        
    def __init__(self, aba = None, root_arg = None, arg_index = 0):
        self.graphs = [nx.DiGraph()] # Directed graph
        
        self.root_arg = root_arg
        self.arg_index = arg_index
        self.__aba = aba
        
        self.__history = [[]]
        self.__depth = [0]

        self.__current_index = 0
        self.graphs[0].add_node(root_arg)
        self.__add_label(0, root_arg, DT_PROPONENT)
        self.__depth[0] += 1
        
        self.is_grounded = [True]
        self.is_admissible = [True]
        self.is_complete = [None]
        self.is_ideal = [None]
        
        logging.debug("Dispute tree for '%s'", root_arg.root)
        self.__propagate_tree_proponent(0, root_arg)
        
        logging.debug(self.graphs[0].nodes(data = True))
        logging.debug(self.graphs[0].edges())
        
        logging.debug("\n")
        logging.debug("Admissible?      %s", self.is_admissible)
        logging.debug("Grounded?        %s", self.is_grounded)
        logging.debug('End dispute tree\n\n')
    
    
    def __propagate_tree_proponent(self, index, node):
        """
        Attack by opponents
        
        Add (zero or more) Opponent_nodes to Proponent_node as a child
        """
        self.__current_index = index

        if len(node.assumptions) > 1:
            #level_graphs_copy = pickle.loads(pickle.dumps(self.graphs[index], -1))
            #level_graphs_copy = nx.DiGraph(self.graphs[index].copy()) 
            level_graphs_copy = nx.DiGraph(self.graphs[index]) # shallow copy; TODO, check if still okay; deep copy is too slow
            level_history_copy = ujson.loads(ujson.dumps(self.__history[index]))
            level_depth_copy = ujson.loads(ujson.dumps(self.__depth[index]))
            level_is_grounded_copy = ujson.loads(ujson.dumps(self.is_grounded[index]))
            level_is_admissible_copy = ujson.loads(ujson.dumps(self.is_admissible[index]))
        

        for idx, assumptions in enumerate(node.assumptions):
            if idx > 0: # "OR" branch, create new dispute tree
                #self.graphs.append(level_graphs_copy.copy()) # normal copy
                #self.graphs.append(pickle.loads(pickle.dumps(level_graphs_copy, -1)))
                self.graphs.append(nx.DiGraph(level_graphs_copy)) # shallow copy
                self.__history.append(ujson.loads(ujson.dumps(level_history_copy)))
                self.__depth.append(ujson.loads(ujson.dumps(level_depth_copy)))
                self.is_grounded.append(ujson.loads(ujson.dumps(level_is_grounded_copy)))
                self.is_admissible.append(ujson.loads(ujson.dumps(level_is_admissible_copy)))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__current_index += 1
                
            for assumption, symbol in assumptions.items():
                opponent_node, i = self.__aba.get_argument(symbol, idx)
                if opponent_node is None:
                    continue
                logging.debug("Opp node <%s> attacking assumption <%s> of Pro node <%s>", opponent_node.root, assumption, node.root)
                
                
                self.graphs[self.__current_index].add_edge(node, opponent_node, text_label = "Opponent node <%s> attacking assumption <%s> of Proponent node <%s>" % (opponent_node.root, assumption, node.root))
                self.__add_label(self.__current_index, opponent_node, DT_OPPONENT, assumption_index=idx)

                if self.__is_infinity(self.__current_index, opponent_node, DT_OPPONENT):
                    break
                
                self.__depth[self.__current_index] += 1
                self.__history[self.__current_index].append([opponent_node.root, DT_OPPONENT])
                self.__propagate_tree_opponent(self.__current_index, opponent_node)
                self.__history[self.__current_index].pop()
                self.__depth[self.__current_index] -= 1
        
    def __propagate_tree_opponent(self, index, node):
        """
        Counter-attack by proponent
        
        Add one Proponent_node to Opponent_node as a child
        
        Question: should we choose a proponent child such that infinity tree is avoided?
            >> Will not happen, as the ABA contraries is a "total function", meaning that for one assumption, it is guaranteed that there is only one argument that can attack this assumption.
        """
        self.__current_index = index
        for idx, assumptions in enumerate(node.assumptions):
            if idx > 0: # "OR" branch, create new dispute tree
                #self.graphs.append(self.graphs[index].copy()) # normal copy
                self.graphs.append(nx.DiGraph(self.graphs[index])) # shallow copy
                #self.graphs.append(pickle.loads(pickle.dumps(self.graphs[index], -1)))
                self.__history.append(ujson.loads(ujson.dumps(self.__history[index])))
                self.__depth.append(ujson.loads(ujson.dumps(self.__depth[index])))
                self.is_grounded.append(ujson.loads(ujson.dumps(self.is_grounded[index])))
                self.is_admissible.append(ujson.loads(ujson.dumps(self.is_admissible[index])))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__current_index += 1
                
            for assumption, symbol in assumptions.items():
                proponent_node, i = self.__aba.get_argument(symbol, idx)
                if proponent_node is None:
                    continue
                logging.debug("Pro node <%s> attacking assumption <%s> of Opp node <%s>", proponent_node.root, assumption, node.root)
                
                self.graphs[self.__current_index].add_edge(node, proponent_node, text_label = "Proponent node <%s> attacking assumption <%s> of Opponent node <%s>" % (proponent_node.root, assumption, node.root))
                self.__add_label(self.__current_index, proponent_node, DT_PROPONENT, assumption_index=idx)
                
                if self.__is_infinity(self.__current_index, proponent_node, DT_PROPONENT):
                    break
                
                self.__depth[self.__current_index] += 1
                self.__history[self.__current_index].append([proponent_node.root, DT_PROPONENT])
                self.__propagate_tree_proponent(self.__current_index, proponent_node)
                self.__history[self.__current_index].pop()
                self.__depth[self.__current_index] -= 1
                
                break
        
    def __is_infinity(self, index, node, label):
        logging.debug("<%s, %s, %s>, history: %s", index, node, label, self.__history[index])
        
        value = False
        # for history_node, history_label in self.__history[index]:
        #     if history_node == node.root and history_label == label:
        #         value = True
        #         break
        value = [node.root, label] in self.__history[index]
        if value:
            logging.debug("Infinity detected in node <%s> of <%s, %s>", node.root, index, label)
            self.is_grounded[index] = False
            
        return value
            
        
    def __add_label(self, index, node, label, assumption_index = 0):
        if 'label' in self.graphs[index].node[node]:
            logging.debug("Label already present in node <%s>", node.root)
            if self.graphs[index].node[node]['label'] != label:
                logging.debug("Changing label of node <%s> from <%s> to <%s>", node.root, self.graphs[index].node[node]['label'], label)
                self.is_admissible[index] = False
        self.graphs[index].node[node]['label'] = label
        self.graphs[index].node[node]['text_label'] = "(%s) Argument %s" % (label, node.root)

        if len(node.assumptions[assumption_index]) > 0:
            self.graphs[index].node[node]['text_label'] += "\nwith assumption(s): %s" % (", ".join(node.assumptions[assumption_index]))
        if 'depth' not in self.graphs[index].node[node]:
            self.graphs[index].node[node]['depth'] = self.__depth
            logging.debug("Tree depth of node <%s> is <%s>", node.root, self.__depth)