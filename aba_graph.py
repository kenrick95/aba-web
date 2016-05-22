import networkx as nx

class ABA_Graph():
    """
    ABA_Graph
    
    An ABA_Graph object is an argument, i.e. a node, supported by sentences & assumptions
    
    """
        
    def __init__(self, aba = None, parent = None):
        self.graph = nx.DiGraph() # Directed graph
        
        
        self.graph.add_node(parent)
        self.__propagate(aba, parent)
        print(self.graph.nodes())
        print(self.graph.edges())
        
    def __propagate(self, aba, node):
        # find rule in aba.rule to support node
        for rule in aba.rules:
            if rule.result == node:
                for symbol in rule.symbols:
                    self.graph.add_edge(node, symbol)
                    self.__propagate(aba, symbol)
                    # POTENTIAL TODO: may goes into infinite recursion
                    # if finite, hence grounded
        
        