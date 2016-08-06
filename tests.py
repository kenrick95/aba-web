import unittest
from aba.aba_rule import ABA_Rule
from aba.aba import ABA
from aba.aba_parser import ABA_Parser
import logging

"""
activate fyp

python -m unittest

https://docs.python.org/3.4/library/unittest.html
"""

class TestPotentialArgument(unittest.TestCase):
    def setUp(self):
        text = """
        a |- b.
        """
        self.parser = ABA_Parser(text)
        
    def test_parser_rules(self):
        self.assertEqual(self.parser.parse(), [])
        self.assertEqual(self.parser.parsed_assumptions, [])
        self.assertEqual(self.parser.parsed_rules, [ABA_Rule(['a'], 'b')])
        self.assertEqual(self.parser.parsed_contraries, {})

    def test_aba(self):
        self.parser.parse()
        aba = self.parser.construct_aba()

        self.assertCountEqual(aba.symbols, ['a', 'b'])
        self.assertEqual(aba.rules, [ABA_Rule(['a'], 'b')])
        self.assertEqual(aba.assumptions, [])
        self.assertEqual(aba.contraries, {})
        self.assertCountEqual(aba.nonassumptions, ['a', 'b'])
        self.assertEqual(aba.arguments, [])
        self.assertEqual(aba.dispute_trees, [])

class TestCircularOneSymbol(unittest.TestCase):
    def setUp(self):
        self.aba = ABA()
        self.aba.symbols = ('a')
        self.aba.rules.append(ABA_Rule(['a'], 'a'))

        self.aba.infer_assumptions()
    
    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.construct_dispute_trees()
        
        self.assertEqual(self.aba.arguments, [])

class TestAssumptionWithoutContrary(unittest.TestCase):
    def test_1(self):
        raw = """
        assumption(a).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        self.assertRaises(Exception, parser.construct_aba)
    
    def test_2(self):
        raw = """
        assumption(a).
        assumption(b).
        contrary(a, b).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        self.assertRaises(Exception, parser.construct_aba)

    def test_3(self):
        raw = """
        assumption(a).
        assumption(b).
        contrary(a, b).
        contrary(b, a).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()

        self.assertCountEqual([x.root for x in aba.arguments], ['a', 'b'])
    
    def test_4(self):
        raw = """
        assumption(a).
        contrary(a, b).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x.root for x in aba.arguments], ['a'])


class TestAssumptionOnlyArguments(unittest.TestCase):
    def setUp(self):
        raw = """
        assumption(a).
        assumption(b).
        assumption(c).

        contrary(a, b).
        contrary(b, c).
        contrary(c, a).
        """

        parser = ABA_Parser(raw)
        parser.parse()
        self.aba = parser.construct_aba()

    def test_arguments(self):
        self.assertCountEqual([x.root for x in self.aba.arguments], ['a', 'b', 'c'])


class TestCircularTwoSymbols(unittest.TestCase):
    def setUp(self):
        self.aba = ABA()
        self.aba.symbols = ('a', 'b')
        self.aba.rules.append(ABA_Rule(['a'], 'b'))
        self.aba.rules.append(ABA_Rule(['b'], 'a'))

        self.aba.infer_assumptions()
    
    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.construct_dispute_trees()

        self.assertEqual(self.aba.arguments, [])
        
class TestCircularTwoSymbolsAndOneRealArgument(unittest.TestCase):
    def setUp(self):
        self.aba = ABA()
        self.aba.symbols = ('a', 'b', 'c')
        self.aba.rules.append(ABA_Rule(['a'], 'b'))
        self.aba.rules.append(ABA_Rule(['b'], 'a'))
        self.aba.rules.append(ABA_Rule([None], 'c'))

        self.aba.infer_assumptions()
    
    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.construct_dispute_trees()

        self.assertEqual(self.aba.arguments[0].root, 'c')


class TestParser(unittest.TestCase):
    def setUp(self):
        text = """
        assumption(xz).
        a |- b.
        c , ded |- ef.
        |- g.
        contrary(a, z).
        contrary(ded, pos).
        """
        self.parser = ABA_Parser(text)
        
    def test_parser_rules(self):
        self.assertEqual(self.parser.parse(), [])
        self.assertEqual(self.parser.parsed_assumptions, ['xz'])
        self.assertEqual(self.parser.parsed_rules[0], ABA_Rule(['a'], 'b'))
        self.assertEqual(self.parser.parsed_rules[1], ABA_Rule(['c', 'ded'], 'ef'))
        self.assertEqual(self.parser.parsed_rules[2], ABA_Rule([None], 'g'))
        self.assertEqual(self.parser.parsed_contraries['a'], 'z')

class TestCraven1(unittest.TestCase):
    """
    This test is adapted from Example 1 of Craven, Toni (2016) paper

    |- q.
    q, r |- p.
    a |- r.
    b |- s.
    contrary(a, s).
    contrary(b, p).

    """
    def setUp(self):
        #logging.basicConfig(filename='TestCraven1.log',level=logging.DEBUG) 
    
        self.aba = ABA()
        self.aba.symbols = ('p', 'q', 'r', 's', 'a', 'b')
        self.aba.rules.append(ABA_Rule(['q', 'r'], 'p'))
        self.aba.rules.append(ABA_Rule([None], 'q')) # ground truth, not assumption
        self.aba.rules.append(ABA_Rule(['a'], 'r'))
        self.aba.rules.append(ABA_Rule(['b'], 's'))
        
        # for each assumptions, what node can attack it?
        # "total function": synonym for function, i.e. one assumption can only be attacked by one sentence
        self.aba.contraries['a'] = 's'
        self.aba.contraries['b'] = 'p'

        # assumptions are determined from contraries
        self.aba.infer_assumptions()
        
        self.aba.construct_arguments()
        
        self.aba.construct_dispute_trees()
        

    def test_conflict_free(self):
        for argument in self.aba.arguments:
            self.assertEqual(argument.is_conflict_free, True)
            
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