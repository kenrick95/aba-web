#!/usr/bin/python
# -*- coding: utf-8 -*-
import networkx as nx
from .aba_constants import *
import logging
import copy

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
        for idx, assumptions in enumerate(node.assumptions):
            if idx > 0: # "OR" branch, create new dispute tree
                self.graphs.append(self.graphs[index].copy())
                self.__history.append(copy.deepcopy(self.__history[index]))
                self.__depth.append(copy.deepcopy(self.__depth[index]))
                self.is_grounded.append(copy.deepcopy(self.is_grounded[index]))
                self.is_admissible.append(copy.deepcopy(self.is_admissible[index]))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__current_index += 1
                
            for assumption, symbol in assumptions.items():
                opponent_node, i = self.__aba.get_argument(symbol, idx)
                if opponent_node is None:
                    continue
                logging.debug("Opp node <%s> attacking assumption <%s> of Pro node <%s>", opponent_node.root, assumption, node.root)
                
                
                self.graphs[self.__current_index].add_edge(node, opponent_node, text_label = "Opponent node <%s> attacking assumption <%s> of Proponent node <%s>" % (opponent_node.root, assumption, node.root))
                self.__add_label(self.__current_index, opponent_node, DT_OPPONENT)
                
                self.__depth[self.__current_index] += 1
                self.__history[self.__current_index].append((opponent_node, DT_OPPONENT))
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
                self.graphs.append(self.graphs[index].copy())
                self.__history.append(copy.deepcopy(self.__history[index]))
                self.__depth.append(copy.deepcopy(self.__depth[index]))
                self.is_grounded.append(copy.deepcopy(self.is_grounded[index]))
                self.is_admissible.append(copy.deepcopy(self.is_admissible[index]))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__current_index += 1
                
            for assumption, symbol in assumptions.items():
                proponent_node, i = self.__aba.get_argument(symbol, idx)
                if proponent_node is None:
                    continue
                logging.debug("Pro node <%s> attacking assumption <%s> of Opp node <%s>", proponent_node.root, assumption, node.root)
                
                self.graphs[self.__current_index].add_edge(node, proponent_node, text_label = "Proponent node <%s> attacking assumption <%s> of Opponent node <%s>" % (proponent_node.root, assumption, node.root))
                self.__add_label(self.__current_index, proponent_node, DT_PROPONENT)
                
                if self.__is_infinity(self.__current_index, proponent_node, DT_PROPONENT):
                    break
                
                self.__depth[self.__current_index] += 1
                self.__history[self.__current_index].append((proponent_node, DT_PROPONENT))
                self.__propagate_tree_proponent(self.__current_index, proponent_node)
                self.__history[self.__current_index].pop()
                self.__depth[self.__current_index] -= 1
                
                break
        
    def __is_infinity(self, index, node, label):
        value = (node, label) in self.__history[index]
        if value:
            logging.debug("Infinity detected in node <%s> of <%s, %s>", node.root, index, label)
            self.is_grounded[index] = False
            
        return value
            
        
    def __add_label(self, index, node, label):
        if 'label' in self.graphs[index].node[node]:
            logging.debug("Label already present in node <%s>", node.root)
            if self.graphs[index].node[node]['label'] != label:
                logging.debug("Changing label of node <%s> from <%s> to <%s>", node.root, self.graphs[index].node[node]['label'], label)
                self.is_admissible[index] = False
        self.graphs[index].node[node]['label'] = label
        self.graphs[index].node[node]['text_label'] = "(%s) Argument %s" % (label, node.root)

        if len(node.assumptions[index]) > 0:
            self.graphs[index].node[node]['text_label'] += "\nwith assumption(s): %s" % (", ".join(node.assumptions[index]))
        if 'depth' not in self.graphs[index].node[node]:
            self.graphs[index].node[node]['depth'] = self.__depth
            logging.debug("Tree depth of node <%s> is <%s>", node.root, self.__depth)