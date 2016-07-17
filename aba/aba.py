from .aba_rule import ABA_Rule
from .aba_graph import ABA_Graph
from .aba_dispute_tree import ABA_Dispute_Tree
from .aba_constants import *
import networkx as nx
import logging

class ABA():
    """
    ABA: Assumption-based Argumentation, consists of
    - L: sentences = R + A
    - R: inference rules <ABA_Rules>
    - A: assumptions <ABA_Rules, where rhs = None>
        in flat-ABA, A is all symbols that cannot be derived using R
    - c: contrary set: mapping from A to L; which assumptions "attacks" another sentences
    """
    def __init__(self):
        self.symbols = []
        self.rules = []
        self.assumptions = []
        self.contraries = dict()
        self.nonassumptions = []
        
        self.arguments = []
        self.dispute_trees = []
        
    def infer_assumptions(self):
        self.nonassumptions = list(self.symbols)

        for key in self.contraries:
            self.assumptions.append(key)
        
        for assumption in self.assumptions:
            if assumption in self.nonassumptions:
                self.nonassumptions.remove(assumption)
                
    def construct_arguments(self):
        for symbol in self.symbols:
            potential_argument = ABA_Graph(self, symbol)
            if potential_argument.is_actual_argument():
                self.arguments.append(potential_argument)
            
    def construct_dispute_trees(self):
        for symbol in self.symbols:
            argument = self.get_argument(symbol)
            if argument:
                self.dispute_trees.append(ABA_Dispute_Tree(self, argument))
        self.__determine_dispute_tree_is_ideal()
        self.__determine_dispute_tree_is_complete()

    def __determine_dispute_tree_is_ideal(self):
        for tree in self.dispute_trees:
            ideal = False
            if tree.is_admissible:
                ideal = True
                for node in tree.graph.nodes(data = True):
                    if node[1]['label'] == DT_OPPONENT:
                        opponent_dispute_tree = self.get_dispute_tree(node[0].root)
                        if opponent_dispute_tree and opponent_dispute_tree.is_admissible:
                            ideal = False
                            break
            tree.is_ideal = ideal
            logging.debug("Dispute Tree <%s> is ideal: %s", tree.root_arg.root, tree.is_ideal)

    def __determine_dispute_tree_is_complete(self):
        for tree in self.dispute_trees:
            complete = False
            if tree.is_admissible:
                complete = True
                if not tree.is_grounded: # if tree is grounded, it is guaranteed to be complete
                    attackers = tree.graph.successors(tree.root_arg)
                    defendable_attackers = []
                    # TODO: I feel uneasy about this loop
                    # Maybe what I should do is to get all arguments root_arg can attack --> let x
                    # Then get all arguments that can be attacked by x --> let y
                    # If ALL y inside root_arg, then complete
                    for attacker in attackers:
                        defenders = tree.graph.successors(attacker)
                        if defenders and defenders[0].root in tree.root_arg.graph.nodes():
                            defendable_attackers.append(attacker)
                    logging.debug("DT<%s> Defendable attackers: %s", tree.root_arg.root, defendable_attackers)
                    
                    defendable_arguments = []
                    for attacker in defendable_attackers:
                        # given an argument, which other arguments it can attack?
                        for argument in self.arguments:
                            if attacker.root == argument.root:
                                continue
                            attackable = False
                            for assumption, symbol in argument.assumptions.items():
                                if symbol == attacker.root:
                                    attackable = True
                                    break
                            if attackable:
                                defendable_arguments.append(argument)

                    all_in_argument = True
                    for argument in defendable_arguments:
                        if argument.root not in tree.root_arg.graph.nodes():
                            all_in_argument = False
                            break
                    complete = all_in_argument
                    logging.debug("DT<%s> Defendable arguments: %s", tree.root_arg.root, defendable_arguments)


            tree.is_complete = complete
            logging.debug("Dispute Tree <%s> is complete: %s", tree.root_arg.root, tree.is_complete)

            
    def get_argument(self, symbol):
        argument = [x for x in self.arguments if x.root == symbol]
        if len(argument) > 0:
            return argument[0]
        return None
    
    def get_dispute_tree(self, symbol):
        dispute_tree = [x for x in self.dispute_trees if x.root_arg.root == symbol]
        if len(dispute_tree) > 0:
            return dispute_tree[0]
        return None
        
    def get_combined_argument_graph(self):
        combined = nx.DiGraph()
        for argument in self.arguments:
            arg_root = argument.root
            if arg_root is None:
                arg_root = "τ"
            for node in argument.graph.nodes():
                if node is None:
                    node = "τ"
                combined.add_node(node + "_" + arg_root, group = arg_root)
            for edge in argument.graph.edges():
                edge0, edge1 = edge
                if edge0 is None:
                    edge0 = "τ"
                if edge1 is None:
                    edge1 = "τ"
                combined.add_edge(edge0 + "_" + arg_root, edge1 + "_" + arg_root)
            
        return combined
        