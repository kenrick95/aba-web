#!/usr/bin/python
# -*- coding: utf-8 -*-
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
logging.basicConfig(filename='Tests.log',level=logging.DEBUG) 

class TestPotentialArgument(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())

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

class TestRealAndPartialArguments(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())

        self.aba = ABA()
        self.aba.symbols = ('a', 'b', 'c')
        self.aba.rules.append(ABA_Rule(['b'], 'a'))
        self.aba.rules.append(ABA_Rule(['c'], 'a'))
        self.aba.rules.append(ABA_Rule([None], 'b'))

        self.aba.infer_assumptions()
    
    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.construct_dispute_trees()
        
        self.assertEqual(self.aba.potential_arguments[0][0].root, 'a')
        self.assertEqual(self.aba.potential_arguments[1][0].root, 'a')
        self.assertEqual(self.aba.potential_arguments[2][0].root, 'b')
        self.assertEqual(self.aba.potential_arguments[3][0].root, 'c')
        self.assertEqual(self.aba.arguments[0][0].root, 'a')
        self.assertEqual(self.aba.arguments[1][0].root, 'b')

class TestRealAndPartialArgumentsWithContrary(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())

        self.aba = ABA()
        self.aba.symbols = ('a', 'b', 'c')
        self.aba.rules.append(ABA_Rule(['b'], 'a'))
        self.aba.rules.append(ABA_Rule(['c'], 'a'))
        self.aba.rules.append(ABA_Rule([None], 'b'))
        self.aba.contraries['c'] = 'b'

        self.aba.infer_assumptions()
    
    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.construct_dispute_trees()
        
        self.assertEqual([x[0].root for x in self.aba.potential_arguments], ['a', 'a', 'b', 'c'])
        self.assertEqual([x[0].root for x in self.aba.arguments], ['a', 'a', 'b', 'c'])


class TestCircularOneSymbol(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())
        
        self.aba = ABA()
        self.aba.symbols = ('a')
        self.aba.rules.append(ABA_Rule(['a'], 'a'))

        self.aba.infer_assumptions()
    
    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.construct_dispute_trees()
        
        self.assertEqual(self.aba.arguments, [])

class TestAssumptionWithoutContrary(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())

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

        self.assertCountEqual([x[0].root for x in aba.arguments], ['a', 'b'])
    
    def test_4(self):
        raw = """
        assumption(a).
        contrary(a, b).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['a'])


class TestAssumptionOnlyArguments(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())

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
        self.assertCountEqual([x[0].root for x in self.aba.arguments], ['a', 'b', 'c'])

class TestMultipleDisputeTrees(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())
    
    def test_1(self):
        """
        a1 |- c.
        a2 |- c.
        b1 |- d.
        b2 |- d.
        contrary(a1, d).
        contrary(a2, d).
        contrary(b1, c).
        contrary(b2, c).
        """

        aba = ABA()
        aba.symbols = ('a1', 'a2', 'b1', 'b2', 'c', 'd')
        aba.rules.append(ABA_Rule(['a1'], 'c'))
        aba.rules.append(ABA_Rule(['a2'], 'c'))
        aba.rules.append(ABA_Rule(['b1'], 'd'))
        aba.rules.append(ABA_Rule(['b2'], 'd'))
        aba.contraries['a1'] = 'd'
        aba.contraries['a2'] = 'd'
        aba.contraries['b1'] = 'c'
        aba.contraries['b2'] = 'c'

        aba.infer_assumptions()
        aba.construct_arguments()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['a1', 'a2', 'b1', 'b2', 'c', 'c', 'd', 'd'])


        aba.construct_dispute_trees()

        


class TestCircularTwoSymbols(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())

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
        logging.debug(self.id())
        
        self.aba = ABA()
        self.aba.symbols = ('a', 'b', 'c')
        self.aba.rules.append(ABA_Rule(['a'], 'b'))
        self.aba.rules.append(ABA_Rule(['b'], 'a'))
        self.aba.rules.append(ABA_Rule([None], 'c'))

        self.aba.infer_assumptions()
    
    def test_successful_inference(self):
        self.aba.construct_arguments()
        self.aba.construct_dispute_trees()

        self.assertEqual(self.aba.arguments[0][0].root, 'c')


class TestParser(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())
        
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

class TestDungMancarellaToni(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())
        
    def test_1(self):
        raw = """
        assumption(a).
        assumption(b).
        contrary(a, b).
        contrary(b, a).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        for argument, i in aba.arguments:
            self.assertEqual(argument.is_conflict_free, [True])
            self.assertEqual(argument.is_stable, [True])
        for dt in aba.dispute_trees:
            self.assertEqual(dt.is_admissible, [True])
            self.assertEqual(dt.is_complete, [True])
            self.assertEqual(dt.is_grounded, [False])
            self.assertEqual(dt.is_ideal, [False])

    def test_2(self):
        raw = """
        assumption(a).
        assumption(b).
        contrary(a, a).
        contrary(b, a).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()

        self.assertEqual(aba.get_argument('a')[0].is_conflict_free, [False])
        self.assertEqual(aba.get_argument('a')[0].is_stable, [False])
        self.assertEqual(aba.get_argument('b')[0].is_conflict_free, [True])
        self.assertEqual(aba.get_argument('b')[0].is_stable, [False])

        for dt in aba.dispute_trees:
            self.assertEqual(dt.is_admissible, [False])
            self.assertEqual(dt.is_complete, [False])
            self.assertEqual(dt.is_grounded, [False])
            self.assertEqual(dt.is_ideal, [False])

        

class TestCraven(unittest.TestCase):
    def setUp(self):
        logging.debug(self.id())
        
    def test_example_1(self):
        """
        Adapted from Example 1 of Craven, Toni (2016) paper

        |- q.
        q, r |- p.
        a |- r.
        b |- s.
        contrary(a, s).
        contrary(b, p).

        """
        aba = ABA()
        aba.symbols = ('p', 'q', 'r', 's', 'a', 'b')
        aba.rules.append(ABA_Rule(['q', 'r'], 'p'))
        aba.rules.append(ABA_Rule([None], 'q')) # ground truth, not assumption
        aba.rules.append(ABA_Rule(['a'], 'r'))
        aba.rules.append(ABA_Rule(['b'], 's'))
        
        # for each assumptions, what node can attack it?
        # "total function": synonym for function, i.e. one assumption can only be attacked by one sentence
        aba.contraries['a'] = 's'
        aba.contraries['b'] = 'p'

        # assumptions are determined from contraries
        aba.infer_assumptions()
        aba.construct_arguments()
        aba.construct_dispute_trees()
        

        for argument, i in aba.arguments:
            self.assertEqual(argument.is_conflict_free, [True])
        
        for dispute_tree in aba.dispute_trees:
            self.assertEqual(dispute_tree.is_admissible, [True])
        
        for dispute_tree in aba.dispute_trees:
            if dispute_tree.root_arg.root == 'q':
                self.assertEqual(dispute_tree.is_grounded, [True])
            else:
                self.assertEqual(dispute_tree.is_grounded, [False])
    def test_example_2(self):
        """
        Adapted from Example 2 of Craven, Toni (2016) paper
        Showing "circularity" of argument graph and hence can't be constructed as an actual argument
        """

        raw = """
        q, r |- p.
        b |- p.
        p |- q.
        r |- q.
        a |- r.
        b |- r.
        r |- s.
        contrary(a, x).
        contrary(b, x).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['a', 'b', 'r', 'r', 's', 's', 'p', 'p', 'p', 'p', 'q', 'q', 'q'])
    def test_example_3(self):
        """
        Adapted from Example 3 of Craven, Toni (2016) paper
        """

        raw = """
        q, r |- p.
        s |- q.
        s, a |- r.
        |- s.
        r |- t.
        contrary(a, x).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['t', 'p', 'q', 'r', 's', 'a'])

    def test_example_4(self):
        """
        Adapted from Example 4 of Craven, Toni (2016) paper
        """

        raw = """
        a, q |- p.
        b, r |- p.
        p |- q.
        b |- r.
        c |- r.
        contrary(a, z).
        contrary(b, z).
        contrary(c, z).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['r', 'r', 'b', 'c', 'a', 'p', 'p', 'q', 'q'])

    def test_example_6(self):
        """
        Adapted from Example 6 of Craven, Toni (2016) paper
        """

        raw = """
        p |- p.
        a |- p.
        contrary(a, x).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['a', 'p'])

    def test_example_7(self):
        """
        Adapted from Example 7 of Craven, Toni (2016) paper
        """

        raw = """
        a |- p.
        b |- p.
        y |- x.
        c |- y.
        contrary(a, y).
        contrary(b, z).
        contrary(c, y).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'p', 'x', 'y', 'a', 'b', 'c'])

    def test_example_8(self):
        """
        Adapted from Example 8 of Craven, Toni (2016) paper
        """

        raw = """
        a |- p.
        p |- q.
        b |- r.
        contrary(a, r).
        contrary(b, p).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'q', 'r', 'a', 'b'])

        for argument, i in aba.arguments:
            self.assertEqual(argument.is_conflict_free, [True])
        
        for dispute_tree in aba.dispute_trees:
            self.assertEqual(dispute_tree.is_admissible, [True])
            
            if dispute_tree.root_arg.root == 'p':
                self.assertEqual(dispute_tree.is_complete, [False])
            else:
                self.assertEqual(dispute_tree.is_complete, [True])
            
            self.assertEqual(dispute_tree.is_grounded, [False])

    def test_example_9(self):
        """
        Adapted from Example 9 of Craven, Toni (2016) paper
        """

        raw = """
        a |- p.
        p, b |- q.
        p, d |- q.
        c |- y.
        e |- z.
        contrary(a, x).
        contrary(b, y).
        contrary(c, q).
        contrary(d, z).
        contrary(e, p).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'q', 'q', 'y', 'z', 'a', 'b', 'c', 'd', 'e'])

        # for argument, i in aba.arguments:
        #     self.assertEqual(argument.is_conflict_free, [True])

    def test_example_10(self):
        """
        Adapted from Example 10 of Craven, Toni (2016) paper
        """

        raw = """
        a |- p.
        b |- p.
        c |- q.
        d |- r.
        assumption(e).
        assumption(f).
        contrary(a, x).
        contrary(b, x).
        contrary(c, p).
        contrary(d, q).
        contrary(e, f).
        contrary(f, e).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'p', 'q', 'r', 'a', 'b', 'c', 'd', 'e', 'f'])

        # for argument, i in aba.arguments:
        #     self.assertEqual(argument.is_conflict_free, [True])

    def test_example_11(self):
        """
        Adapted from Example 11 of Craven, Toni (2016) paper
        """

        raw = """
        q, r |- p.
        a |- q.
        t, a, b |- r.
        b |- s.
        |- t.
        contrary(a, x).
        contrary(b, y).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'q', 'r', 's', 't', 'a', 'b'])
    
    def test_example_12(self):
        """
        Adapted from Example 12 of Craven, Toni (2016) paper
        """

        raw = """
        a |- p.
        a |- q.
        b |- q.
        contrary(a, z).
        contrary(b, z).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'q', 'q', 'a', 'b'])

    def test_example_13(self):
        """
        Adapted from Example 13 of Craven, Toni (2016) paper
        """

        raw = """
        b |- p.
        |- q.
        assumption(a).
        contrary(a, p).
        contrary(b, q).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'q', 'a', 'b'])

    def test_example_14(self):
        """
        Adapted from Example 14 of Craven, Toni (2016) paper
        TODO: Shouldn't 'p' still be an argument with "a |- p" only?
        """

        raw = """
        q |- p.
        a |- p.
        contrary(a, z).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['p', 'a'])


    def test_example_15(self):
        """
        Adapted from Example 15 of Craven, Toni (2016) paper
        """

        raw = """
        a |- p.
        b, c |- z.
        a |- q.
        |- r.
        contrary(a, z).
        contrary(b, q).
        contrary(c, r).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['a', 'b' , 'c', 'p', 'q', 'r', 'z'])

    def test_example_16(self):
        """
        Adapted from Example 16 of Craven, Toni (2016) paper
        """

        raw = """
        q |- p.
        a |- q.
        p |- r.
        contrary(a, b).
        contrary(b, r).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['a', 'p', 'q', 'r'])

    def test_example_17(self):
        """
        Adapted from Example 17 of Craven, Toni (2016) paper
        """

        raw = """
        b, r |- p.
        b, s |- p.
        |- q.
        assumption(a).
        contrary(a, p).
        contrary(b, q).
        """
        parser = ABA_Parser(raw)
        parser.parse()
        aba = parser.construct_aba()
        self.assertCountEqual([x[0].root for x in aba.arguments], ['q', 'a', 'b'])



if __name__ == '__main__':
    unittest.main()