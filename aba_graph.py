import networkx as nx

class ABA_Graph():
    """
    An ABA_Graph object is an argument, i.e. a node, supported by sentences & assumptions
    
    """
        
    def __init__(self, aba = None, root = None):
        self.graph = nx.DiGraph() # Directed graph
        
        self.root = root
        self.aba = aba
        
        self.graph.add_node(root)
        self.__propagate(root)
        
        self.assumptions = {}
        self.__propagate_assumptions()
        
    def __propagate(self, node):
        # find rule in aba.rule to support node
        for rule in self.aba.rules:
            if rule.result == node:
                for symbol in rule.symbols:
                    self.graph.add_edge(node, symbol)
                    self.__propagate(symbol)
                    
    def __propagate_assumptions(self):
        for assumption, symbol in self.aba.contraries.items():
            if assumption in self.graph.nodes():
                self.assumptions[assumption] = symbol
    
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
        
    def __str__(self):
        return "Argument '%s'" % self.root
        
    def __repr__(self):
        return str(self)