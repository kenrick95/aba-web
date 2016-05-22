import networkx as nx
from aba_constants import *

class ABA_Dispute_Tree():
    """
    ABA_Dispute_Tree
    
    Vertices: <argument + label>
    Edges: attacks
    
    """
        
    def __init__(self, aba = None, parent = None):
        self.graph = nx.DiGraph() # Directed graph
        
        self.parent = parent
        self.aba = aba
        
        self.graph.add_node(parent)
        self.graph.node[parent]['label'] = DT_PROPONENT
        
    