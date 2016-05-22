import unittest
from aba_rule import ABA_Rule
from aba import ABA
import logging

"""
activate fyp

python -m unittest

https://docs.python.org/3.4/library/unittest.html
"""

class TestCraven1(unittest.TestCase):
    """
    This test is adapted from Example 1 of Craven, Toni (2016) paper
    """
    def setUp(self):
        logging.basicConfig(filename='TestCraven1.log',level=logging.DEBUG) 
    
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
        
        self.aba.construct_arguments()
        
        self.aba.construct_dispute_trees()
        

    def test_conflict_free(self):
        for argument in self.aba.arguments:
            self.assertEqual(argument.is_conflict_free(), True)
            
    def test_admissible(self):
        for dispute_tree in self.aba.dispute_trees:
            self.assertEqual(dispute_tree.is_admissible, True)
    
    def test_grounded(self):
        for dispute_tree in self.aba.dispute_trees:
            if dispute_tree.root_arg.root == 'q':
                self.assertEqual(dispute_tree.is_grounded, True)
            else:
                self.assertEqual(dispute_tree.is_grounded, False)

if __name__ == '__main__':
    unittest.main()