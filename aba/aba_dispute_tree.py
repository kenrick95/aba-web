import networkx as nx
from .aba_constants import *
import logging

class ABA_Dispute_Tree():
    """
    ABA_Dispute_Tree
    
    Vertices: <argument + label>
    Edges: attacks
    
    """
        
    def __init__(self, aba = None, root_arg = None):
        self.graph = nx.DiGraph() # Directed graph
        
        self.root_arg = root_arg
        self.aba = aba
        
        self.graph.add_node(root_arg)
        self.graph.node[root_arg]['label'] = DT_PROPONENT
        
        self.is_grounded = True
        self.is_admissible = True
        
        self.__history = []
        
        logging.debug("Dispute tree for '%s'" % root_arg.root)
        self.__propagate_tree_proponent(root_arg)
        
        logging.debug(self.graph.nodes(data = True))
        logging.debug(self.graph.edges())
        
        logging.debug("\n")
        logging.debug("Admissible?      %s" % self.is_admissible)
        logging.debug("Grounded?        %s" % self.is_grounded)
        logging.debug('End dispute tree\n\n')
    
    
    def __propagate_tree_proponent(self, node):
        """
        Attack by opponents
        
        Add (zero or more) Opponent_nodes to Proponent_node as a child
        """
        for assumption, symbol in node.assumptions.items():
            opponent_node = self.aba.get_argument(symbol)
            logging.debug("Opp Node: <%s> attacking assumption <%s> of Pro node <%s>" % (opponent_node.root, assumption, node.root))
            
            
            self.graph.add_edge(node, opponent_node)
            self.__add_label(opponent_node, DT_OPPONENT)
            
            
            self.__history.append((opponent_node, DT_OPPONENT))
            self.__propagate_tree_opponent(opponent_node)
            self.__history.pop()
        
    def __propagate_tree_opponent(self, node):
        """
        Counter-attack by proponent
        
        Add one Proponent_node to Opponent_node as a child
        
        TODO Question: should we choose a proponent child such that infinity tree is avoided?
        """
        for assumption, symbol in node.assumptions.items():
            proponent_node = self.aba.get_argument(symbol)
            logging.debug("Pro Node: <%s> attacking assumption <%s> of Opp node <%s>" % (proponent_node.root, assumption, node.root))
            
            if self.__is_infinity(proponent_node, DT_PROPONENT):
                break
            
            
            self.graph.add_edge(node, proponent_node)
            self.__add_label(proponent_node, DT_PROPONENT)
            
            
            self.__history.append((proponent_node, DT_PROPONENT))
            self.__propagate_tree_proponent(proponent_node)
            self.__history.pop()
            
            break
        
    def __is_infinity(self, node, label):
        value = (node, label) in self.__history
        if value:
            logging.debug("Infinity detected in node <%s> of <%s>"% (node.root, label))
            self.is_grounded = False
            
        return value
            
        
    def __add_label(self, node, label):
        if 'label' in self.graph[node]:
            logging.debug("Label already present in node <%s>" % (node.root))
            if self.graph[node]['label'] != label:
                logging.debug("Changing label of node <%s> from <%s> to <%s>" % (node.root, self.graph[node]['label'], label))
                self.is_admissible = False
        self.graph.node[node]['label'] = label