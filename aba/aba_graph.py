import networkx as nx
import logging

class ABA_Graph():
    """
    An ABA_Graph object is an argument, i.e. a node, supported by sentences & assumptions
    
    """
        
    def __init__(self, aba = None, root = None):
        self.graph = nx.DiGraph() # Directed graph
        
        self.root = root
        self.__aba = aba
        
        self.__history = []
        self.__is_cyclical = False

        self.graph.add_node(root)
        self.__history.append(root)
        self.__propagate(root)
        self.__history.pop()

        self.assumptions = {}
        self.__propagate_assumptions()

        self.is_conflict_free = None
        self.__determine_is_conflict_free()

        self.is_stable = None
        self.__determine_is_stable()
        
    def __propagate(self, node):
        # find rule in aba.rule to support node
        for rule in self.__aba.rules:
            if rule.result == node:
                for symbol in rule.symbols:
                    self.graph.add_edge(node, symbol)
                    if symbol is not None:
                        if symbol in self.__history:
                            self.__is_cyclical = True
                            break
                        self.__history.append(symbol)
                        self.__propagate(symbol)
                        self.__history.pop()
            if self.__is_cyclical:
                break
                    
    def __propagate_assumptions(self):
        for assumption, symbol in self.__aba.contraries.items():
            if assumption in self.graph.nodes():
                # `assumption` is being attacked by `symbol`
                self.assumptions[assumption] = symbol
    
    def __determine_is_conflict_free(self):
        conflict_free = True
        for assumption, attacker in self.__aba.contraries.items():
            if attacker in self.graph.nodes() and assumption in self.graph.nodes():
                conflict_free = False
                break
        self.is_conflict_free = conflict_free
        logging.debug("Argument <%s> is conflict free: %s", self.root, self.is_conflict_free)

    def __determine_is_stable(self):
        stable = False
        if self.is_conflict_free:
            stable = True
            for assumption, attacker in self.__aba.contraries.items():
                if assumption not in self.graph.nodes():
                    if attacker not in self.graph.nodes():
                        stable = False
                        break
        
        self.is_stable = stable
        logging.debug("Argument <%s> is stable: %s", self.root, self.is_stable)

    def __process_is_actual_argument(self, node):
        if self.__is_cyclical:
            return False

        neighbors = self.graph.successors(node)
        if len(neighbors) == 0: # leaf node
            if node is None or node in self.__aba.assumptions:
                return True
            return False
        
        ret = True
        for neighbor in neighbors:
            ret = ret and self.__process_is_actual_argument(neighbor)
        return ret

    def is_actual_argument(self):
        return self.__process_is_actual_argument(self.root)

    def __str__(self):
        return "Argument '%s'" % self.root
        
    def __repr__(self):
        return str(self)