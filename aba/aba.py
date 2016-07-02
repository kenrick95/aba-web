from .aba_rule import ABA_Rule
from .aba_graph import ABA_Graph
from .aba_dispute_tree import ABA_Dispute_Tree
import networkx as nx

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
        
        self.arguments = []
        self.dispute_trees = []
        
    def infer_assumptions(self):
        for key in self.contraries:
            self.assumptions.append(ABA_Rule([key]))
                
    def construct_arguments(self):
        for symbol in self.symbols:
            self.arguments.append(ABA_Graph(self, symbol))
            
    def construct_dispute_trees(self):
        for symbol in self.symbols:
            self.dispute_trees.append(ABA_Dispute_Tree(self, self.get_argument(symbol)))
            
    def get_argument(self, symbol):
        return [x for x in self.arguments if x.root == symbol][0]
    
    def get_dispute_tree(self, symbol):
        return [x for x in self.dispute_trees if x.root_arg.root == symbol][0]
        
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
        