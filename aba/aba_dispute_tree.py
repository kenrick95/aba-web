import networkx as nx
from .aba_constants import *
import logging

class ABA_Dispute_Tree():
    """
    ABA_Dispute_Tree
    
    Vertices: <argument + label>
    Edges: attacks
    
    """
        
    def __init__(self, aba = None, root_arg = None, index = 0):
        self.graph = nx.DiGraph() # Directed graph
        
        self.root_arg = root_arg
        self.__aba = aba
        
        self.__history = []
        self.__depth = 0

        self.graph.add_node(root_arg)
        self.__add_label(root_arg, DT_PROPONENT, index)
        self.__depth += 1
        
        self.is_grounded = True
        self.is_admissible = True
        self.is_complete = None
        self.is_ideal = None
        
        logging.debug("Dispute tree for '%s'", root_arg.root)
        self.__propagate_tree_proponent(root_arg, index)
        
        logging.debug(self.graph.nodes(data = True))
        logging.debug(self.graph.edges())
        
        logging.debug("\n")
        logging.debug("Admissible?      %s", self.is_admissible)
        logging.debug("Grounded?        %s", self.is_grounded)
        logging.debug('End dispute tree\n\n')
    
    
    def __propagate_tree_proponent(self, node, index):
        """
        Attack by opponents
        
        Add (zero or more) Opponent_nodes to Proponent_node as a child
        """
        for assumption, symbol in node.assumptions[index].items():
            opponent_node, i = self.__aba.get_argument(symbol)
            if opponent_node is None:
                continue
            logging.debug("Opp node <%s> attacking assumption <%s> of Pro node <%s>", opponent_node.root, assumption, node.root)
            
            
            self.graph.add_edge(node, opponent_node, text_label = "Opponent node <%s> attacking assumption <%s> of Proponent node <%s>" % (opponent_node.root, assumption, node.root))
            self.__add_label(opponent_node, DT_OPPONENT, index)
            
            self.__depth += 1
            self.__history.append((opponent_node, DT_OPPONENT, index))
            self.__propagate_tree_opponent(opponent_node, index)
            self.__history.pop()
            self.__depth -= 1
        
    def __propagate_tree_opponent(self, node, index):
        """
        Counter-attack by proponent
        
        Add one Proponent_node to Opponent_node as a child
        
        Question: should we choose a proponent child such that infinity tree is avoided?
            >> Will not happen, as the ABA contraries is a "total function", meaning that for one assumption, it is guaranteed that there is only one argument that can attack this assumption.
        """
        for assumption, symbol in node.assumptions[index].items():
            proponent_node, i = self.__aba.get_argument(symbol)
            if proponent_node is None:
                continue
            logging.debug("Pro node <%s> attacking assumption <%s> of Opp node <%s>", proponent_node.root, assumption, node.root)
            
            self.graph.add_edge(node, proponent_node, text_label = "Proponent node <%s> attacking assumption <%s> of Opponent node <%s>" % (proponent_node.root, assumption, node.root))
            self.__add_label(proponent_node, DT_PROPONENT, index)
            
            if self.__is_infinity(proponent_node, DT_PROPONENT, index):
                break
            
            self.__depth += 1
            self.__history.append((proponent_node, DT_PROPONENT, index))
            self.__propagate_tree_proponent(proponent_node, index)
            self.__history.pop()
            self.__depth -= 1
            
            break
        
    def __is_infinity(self, node, label, index):
        value = (node, label, index) in self.__history
        if value:
            logging.debug("Infinity detected in node <%s> of <%s, %s>", node.root, label, index)
            self.is_grounded = False
            
        return value
            
        
    def __add_label(self, node, label, index):
        if 'label' in self.graph.node[node]:
            logging.debug("Label already present in node <%s>", node.root)
            if self.graph.node[node]['label'] != label:
                logging.debug("Changing label of node <%s> from <%s> to <%s>", node.root, self.graph.node[node]['label'], label)
                self.is_admissible = False
        self.graph.node[node]['label'] = label
        self.graph.node[node]['text_label'] = "(%s) Argument %s" % (label, node.root)
        if len(node.assumptions[index]) > 0:
            self.graph.node[node]['text_label'] += "\nwith assumption(s): %s" % (", ".join(node.assumptions[index]))
        if 'depth' not in self.graph.node[node]:
            self.graph.node[node]['depth'] = self.__depth
            logging.debug("Tree depth of node <%s> is <%s>", node.root, self.__depth)