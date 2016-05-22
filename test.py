import unittest
from aba_rule import ABA_Rule
from aba_graph import ABA_Graph
from aba import ABA
from aba_dipute_tree import ABA_Dispute_Tree

"""
activate fyp

python -m unittest
"""

class TestABAGraph(unittest.TestCase):
    """
    https://docs.python.org/3.4/library/unittest.html
    """
    def setUp(self):
        self.aba = ABA()
        self.aba.symbols = ('p', 'q', 'r', 's', 'a', 'b')
        self.aba.rules.append(ABA_Rule(['q', 'r'], 'p'))
        self.aba.rules.append(ABA_Rule([None], 'q')) # ground truth, not assumption
        self.aba.rules.append(ABA_Rule(['a'], 'r'))
        self.aba.rules.append(ABA_Rule(['b'], 's'))
        
        # assumptions are determined from the rules
        self.aba.infer_assumptions()
        
        # for each assumptions, what node can attack it?
        # "total function": synonym for function, i.e. one assumption can only be attacked by one sentence
        self.aba.contraries['a'] = 's'
        self.aba.contraries['b'] = 'p'
        
        # setup an argument
        self.aba_graphs = []
        
        for symbol in self.aba.symbols:
            self.aba_graphs.append(ABA_Graph(self.aba, symbol))
        
        
        self.aba_dispute_trees = []
        adt = ABA_Dispute_Tree(self.aba, self.aba_graphs[0])
        print(adt.graph.nodes(data = True))
        
        self.aba_dispute_trees.append(adt)
        

    def test_conflict_free(self):
        for graph in self.aba_graphs:
            self.assertEqual(graph.is_conflict_free(), True)

if __name__ == '__main__':
    unittest.main()