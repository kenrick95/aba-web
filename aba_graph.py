import networkx as nx

class ABA_Graph():
    """
    ABA_Graph
    
    An ABA_Graph object is an argument, i.e. a node, supported by sentences & assumptions
    
    """
        
    def __init__(self, aba = None, parent = None):
        self.graph = nx.DiGraph() # Directed graph
        
        self.parent = parent
        self.aba = aba
        
        self.graph.add_node(parent)
        self.__propagate(parent)
        
    def __propagate(self, node):
        # find rule in aba.rule to support node
        for rule in self.aba.rules:
            if rule.result == node:
                for symbol in rule.symbols:
                    self.graph.add_edge(node, symbol)
                    self.__propagate(symbol)
                    # POTENTIAL TODO: may goes into infinite recursion
                    # if finite, hence grounded
    
    def is_conflict_free(self):
        conflict_free = True
        for assumption, attacker in self.aba.contraries.items():
            if attacker not in self.graph.nodes():
                continue
            neighbors = self.graph.successors(attacker)

            if assumption in neighbors:
                conflict_free = False
                break
        return conflict_free