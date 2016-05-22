import unittest
from aba_rule import ABA_Rule
from aba_graph import ABA_Graph
from aba import ABA

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
        self.aba.rules.append(ABA_Rule([], 'q')) # ground truth, not assumption
        self.aba.rules.append(ABA_Rule(['a'], 'r'))
        self.aba.rules.append(ABA_Rule(['b'], 's'))
        
        # TODO this shall be determned from the rules
        self.aba.assumptions.append(ABA_Rule(['a']))
        self.aba.assumptions.append(ABA_Rule(['b']))
        
        # for each assumptions, what does it "attack"?
        self.aba.contraries['a'] = 's'
        self.aba.contraries['b'] = 'p'
        
        # setup an argument
        self.aba_graphs = []
        
        for symbol in self.aba.symbols:
            self.aba_graphs.append(ABA_Graph(self.aba, symbol))
        

    def test_admissible(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()