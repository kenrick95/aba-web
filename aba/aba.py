from .aba_rule import ABA_Rule
from .aba_graph import ABA_Graph
from .aba_dispute_tree import ABA_Dispute_Tree

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
        assumptions = {}
        for symbol in self.symbols:
            assumptions[symbol] = True
        
        for rule in self.rules:
            assumptions[rule.result] = False
            
        for symbol in assumptions:
            if assumptions[symbol]:
                self.assumptions.append(ABA_Rule([symbol]))
                
    def construct_arguments(self):
        for symbol in self.symbols:
            self.arguments.append(ABA_Graph(self, symbol))
            
    def construct_dispute_trees(self):
        for symbol in self.symbols:
            self.dispute_trees.append(ABA_Dispute_Tree(self, self.get_argument(symbol)))
            
    def get_argument(self, symbol):
        return [x for x in self.arguments if x.root == symbol][0]