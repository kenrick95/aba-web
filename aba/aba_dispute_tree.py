#!/usr/bin/python
# -*- coding: utf-8 -*-
import networkx as nx
import pickle
import ujson
from .aba_constants import *
import logging
import functools

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

        self.__cache = {}
        # key: <argument, arg_index>;
        # value: {
        #   tree: DT with <argument, arg_index> as root_arg (proponent)
        #   is_grounded:
        #   is_admissible:
        # }


        self.__max_index = 0
        self.graphs[0].add_node(root_arg.root)
        self.__add_label(0, root_arg, DT_PROPONENT)
        self.__depth[0] += 1
        
        self.__found_grounded = False

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
    
    def __handle_leaf(self):
        logging.debug("Leaf, DT <%s, %s>, grounded: %s", self.root_arg, self.__max_index, self.is_grounded)
        self.__found_grounded = functools.reduce(lambda x,y: x or y, self.is_grounded)
        if self.__found_grounded:
            logging.debug("I shall delete the rest")
    
    def __propagate_tree_proponent(self, index, node, arg_idx=0):
        """
        Attack by opponents
        
        Add (zero or more) Opponent_nodes to Proponent_node as a child
        """

        if self.__found_grounded:
            return

        if len(node.assumptions) > 1:
            #level_graphs_copy = nx.DiGraph(self.graphs[index].copy()) # nx deep copy; slow
            level_graphs_copy = pickle.dumps(self.graphs[index], -1) # Python pickle, moderate
            #level_graphs_copy = nx.DiGraph(self.graphs[index]) # nx shallow copy; fast but wrong
            level_history_copy = ujson.dumps(self.__history[index])
            level_depth_copy = ujson.dumps(self.__depth[index])
            level_is_grounded_copy = ujson.dumps(self.is_grounded[index])
            level_is_admissible_copy = ujson.dumps(self.is_admissible[index])

        for idx, assumptions in enumerate(node.assumptions): # For an argument, there may be >1 assumptions from "OR" rules; can do branching
            index_used = index
            if idx > 0: # "OR" branch, create new dispute tree
                #self.graphs.append(level_graphs_copy.copy()) # normal copy
                self.graphs.append(pickle.loads(level_graphs_copy))
                #self.graphs.append(nx.DiGraph(level_graphs_copy)) # shallow copy
                self.__history.append(ujson.loads(level_history_copy))
                self.__depth.append(ujson.loads(level_depth_copy))
                self.is_grounded.append(ujson.loads(level_is_grounded_copy))
                self.is_admissible.append(ujson.loads(level_is_admissible_copy))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__max_index += 1
                index_used = self.__max_index
                if self.__max_index > DT_MAX_BRANCH:
                    logging.error("Too much branching in this DT <%s, %s>; idx: %s, assumptions: %s", self.root_arg, self.__max_index, idx, assumptions)
                    return
                
            logging.debug("ONE idx %s, assumptions %s", idx, assumptions)
            for assumption, symbol in assumptions.items(): # I can branch here, for an assumption attacker, it may be coming from >1 arg idx; but I don't, cause not necessary I guess ._.
                opponent_node, i = self.__aba.get_argument(symbol, 0)
                logging.debug("TWO assumption %s, symbol %s", assumption, symbol)
                if opponent_node is None:
                    logging.debug("THREE opponent_node %s, i %s", opponent_node, i)
                    self.__handle_leaf()
                    if self.__found_grounded:
                        return
                    continue
                logging.debug("Opp node <%s, %d> attacking assumption <%s> of Pro node <%s, %d>", opponent_node.root, i, assumption, node.root, index)
                
                
                self.graphs[index_used].add_edge(node.root, opponent_node.root, text_label = "Opponent node <%s, %d> attacking assumption <%s> of Proponent node <%s, %d>" % (opponent_node.root, i, assumption, node.root, index))
                self.__add_label(index_used, opponent_node, DT_OPPONENT, assumption_index=0)

                if self.__is_infinity(index_used, opponent_node, DT_OPPONENT):
                    break
                
                self.__depth[index_used] += 1
                self.__history[index_used].append([opponent_node.root, DT_OPPONENT])
                self.__propagate_tree_opponent(index_used, opponent_node, i)
                self.__history[index_used].pop()
                self.__depth[index_used] -= 1
        
        
        self.__cache[(node.root, arg_idx)] = {
            "tree": pickle.dumps(self.graphs[index], -1),
            "is_grounded": self.is_grounded[index],
            "is_admissible": self.is_admissible[index],
        }
        
    def __propagate_tree_opponent(self, index, node, arg_idx=0):
        """
        Counter-attack by proponent
        
        Add one Proponent_node to Opponent_node as a child
        
        Question: should we choose a proponent child such that infinity tree is avoided?
            >> Will not happen, as the ABA contraries is a "total function", meaning that for one assumption, it is guaranteed that there is only one argument that can attack this assumption.
        """

        if self.__found_grounded:
            return

        if len(node.assumptions) > 1:
            level_graphs_copy = pickle.dumps(self.graphs[index], -1)
            #level_graphs_copy = nx.DiGraph(self.graphs[index]) # shallow copy;
            level_history_copy = ujson.dumps(self.__history[index])
            level_depth_copy = ujson.dumps(self.__depth[index])
            level_is_grounded_copy = ujson.dumps(self.is_grounded[index])
            level_is_admissible_copy = ujson.dumps(self.is_admissible[index])

        for idx, assumptions in enumerate(node.assumptions):
            index_used = index
            if idx > 0: # "OR" branch, create new dispute tree
                #self.graphs.append(level_graphs_copy.copy()) # normal copy
                self.graphs.append(pickle.loads(level_graphs_copy))
                #self.graphs.append(nx.DiGraph(level_graphs_copy)) # shallow copy
                self.__history.append(ujson.loads(level_history_copy))
                self.__depth.append(ujson.loads(level_depth_copy))
                self.is_grounded.append(ujson.loads(level_is_grounded_copy))
                self.is_admissible.append(ujson.loads(level_is_admissible_copy))
                self.is_complete.append(None)
                self.is_ideal.append(None)
                self.__max_index += 1
                index_used = self.__max_index
                
            for assumption, symbol in assumptions.items():
                proponent_node, i = self.__aba.get_argument(symbol, 0)
                if proponent_node is None:
                    self.__handle_leaf()
                    if self.__found_grounded:
                        return
                    continue
                logging.debug("Pro node <%s, %d> attacking assumption <%s> of Opp node <%s, %d>", proponent_node.root, i, assumption, node.root, index)
                
                # Search for trees generated with root_arg = proponent_node and arg_index = idx; copy and then pluck that tree as the nodes below
                if (proponent_node.root, i) in self.__cache:
                    cached_data = self.__cache[(proponent_node.root, i)]
                    tree_from_cache = pickle.loads(cached_data["tree"])
                    logging.debug("Cache hit [%s, %s], nodes <%s>; edges <%s>;\ncached is_admissible: %s\ncached is_grounded: %s", proponent_node.root, i, tree_from_cache.nodes(), tree_from_cache.edges(), cached_data["is_admissible"], cached_data["is_grounded"])

                    self.graphs[index_used] = nx.compose(self.graphs[index_used], tree_from_cache)
                    self.is_grounded[index_used] &= cached_data["is_grounded"]
                    self.is_admissible[index_used] &= cached_data["is_admissible"]
                    continue
                
                self.graphs[index_used].add_edge(node.root, proponent_node.root, text_label = "Proponent node <%s, %d> attacking assumption <%s> of Opponent node <%s, %d>" % (proponent_node.root, i, assumption, node.root, index))
                self.__add_label(index_used, proponent_node, DT_PROPONENT, assumption_index=0)
                
                if self.__is_infinity(index_used, proponent_node, DT_PROPONENT):
                    break
                
                self.__depth[index_used] += 1
                self.__history[index_used].append([proponent_node.root, DT_PROPONENT])
                self.__propagate_tree_proponent(index_used, proponent_node, i)
                self.__history[index_used].pop()
                self.__depth[index_used] -= 1
                
                break
        
    def __is_infinity(self, index, node, label):
        value = False
        value = [node.root, label] in self.__history[index]
        if value:
            logging.debug("Infinity detected in node <%s, %d> of <%s>", node.root, index, label)
            self.is_grounded[index] = False
            
        return value
            
        
    def __add_label(self, index, node, label, assumption_index = 0):
        if 'label' in self.graphs[index].node[node.root]:
            logging.debug("Label already present in node <%s>", node.root)
            if self.graphs[index].node[node.root]['label'] != label:
                logging.debug("Changing label of node <%s> from <%s> to <%s>", node.root, self.graphs[index].node[node.root]['label'], label)
                self.is_admissible[index] = False
        self.graphs[index].node[node.root]['label'] = label
        self.graphs[index].node[node.root]['text_label'] = "(%s) Argument %s" % (label, node.root)

        if len(node.assumptions[assumption_index]) > 0:
            logging.debug("__add_label node %s, assumption_index: %s, node.assumptions: %s", node, assumption_index, node.assumptions)
            self.graphs[index].node[node.root]['text_label'] += "\nwith assumption(s): %s" % (", ".join(node.assumptions[assumption_index]))
        if 'depth' not in self.graphs[index].node[node.root]:
            self.graphs[index].node[node.root]['depth'] = self.__depth[index]
            logging.debug("Tree depth of node <%s> is <%s>", node.root, self.__depth[index])