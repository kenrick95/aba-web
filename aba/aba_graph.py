import networkx as nx
import logging
import copy

class ABA_Graph():
    """
    An ABA_Graph object is an argument, i.e. a node, supported by sentences & assumptions
    
    """
        
    def __init__(self, aba = None, root = None):
        self.graphs = []

        self.__history = [[]]
        self.__is_cyclical = [False]

        self.assumptions = [{}]
        self.is_conflict_free = [None]
        self.is_stable = [None]
        
        self.root = root
        self.__aba = aba
        self.__current_index = 0

        self.graphs.append(nx.DiGraph())
        self.__branches = 1

        self.graphs[0].add_node(root)
        self.__history[0].append(root)
        self.__propagate(0, root)
        self.__history[0].pop()

        self.__propagate_assumptions()
        self.__determine_is_conflict_free()
        self.__determine_is_stable()
        
    def __propagate(self, index, node):
        self.__current_index = index
        for i, rule in enumerate([x for x in self.__aba.rules if x.result == node]):
            if i > 0: # "OR" branch, create new argument graph
                self.graphs.append(self.graphs[index].copy())
                self.__history.append(copy.deepcopy(self.__history[index]))
                self.__is_cyclical.append(copy.deepcopy(self.__is_cyclical[index]))
                self.assumptions.append({})
                self.is_conflict_free.append(None)
                self.is_stable.append(None)
                self.__current_index += 1
            
            for symbol in rule.symbols:
                self.graphs[self.__current_index].add_edge(node, symbol)
                if symbol is not None:
                    if symbol in self.__history[self.__current_index]:
                        self.__is_cyclical[self.__current_index] = True
                        break
                    self.__history[self.__current_index].append(symbol)
                    self.__propagate(self.__current_index, symbol)
                    self.__history[self.__current_index].pop()
 
    def __propagate_assumptions(self):
        for assumption, symbol in self.__aba.contraries.items():
            for index, graph in enumerate(self.graphs):
                if assumption in graph.nodes():
                    # `assumption` is being attacked by `symbol`
                    self.assumptions[index][assumption] = symbol
    
    def __determine_is_conflict_free(self):
        for index, graph in enumerate(self.graphs):
            conflict_free = True
            for assumption, attacker in self.__aba.contraries.items():
                if attacker in graph.nodes() and assumption in graph.nodes():
                    conflict_free = False
                    break
            self.is_conflict_free[index] = conflict_free
            logging.debug("Argument <%s> index <%d> is conflict free: %s", self.root, index, self.is_conflict_free)

    def __determine_is_stable(self):
        for index, graph in enumerate(self.graphs):
            stable = False
            if self.is_conflict_free[index]:
                stable = True
                for assumption, attacker in self.__aba.contraries.items():
                    if assumption not in graph.nodes():
                        if attacker not in graph.nodes():
                            stable = False
                            break
            
            self.is_stable[index] = stable
            logging.debug("Argument <%s> index <%d> is stable: %s", self.root, index, self.is_stable)

    def __process_is_actual_argument(self, index, node):
        graph = self.graphs[index]
        if self.__is_cyclical[index]:
            return False

        neighbors = graph.successors(node)
        if len(neighbors) == 0: # leaf node
            if node is None or node in self.__aba.assumptions:
                return True
            return False
        
        ret = True
        for neighbor in neighbors:
            ret = ret and self.__process_is_actual_argument(index, neighbor)
        return ret

    def is_actual_argument(self, index = 0):
        return self.__process_is_actual_argument(index, self.root)

    def __str__(self):
        return "Argument '%s'" % self.root
        
    def __repr__(self):
        return str(self)