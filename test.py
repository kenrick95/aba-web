import unittest
from aba_rule import ABA_Rule
from aba_tree import ABA_Tree
from aba import ABA


class TestABATree(unittest.TestCase):
    """
    https://docs.python.org/3.4/library/unittest.html
    """
    def setUp(self):
        self.aba = ABA()
        self.aba.symbols = ('p', 'q', 'r', 's', 'a', 'b')
        self.aba.rules.append(ABA_Rule(['q', 'r'], 'p'))
        self.aba.rules.append(ABA_Rule(None, 'q')) # ground truth, not assumption
        self.aba.rules.append(ABA_Rule(['a'], 'r'))
        self.aba.rules.append(ABA_Rule(['b'], 's'))
        
        self.aba.assumptions.append(ABA_Rule(['a']))
        self.aba.assumptions.append(ABA_Rule(['b']))
        
        self.aba.contraries['a'] = 's'
        self.aba.contraries['b'] = 'p'
        
        self.tree = ABA_Tree()
        self.tree.create_node("Root", "root")
        self.tree.create_node("F1", "f1", parent='root', data = ABA_Rule("a", "b"))
        self.tree.create_node("F2", "f2", parent='root', data = ABA_Rule("a"))
        print(self.tree.to_json(with_data=True))

    def test_admissible(self):
        self.assertEqual(self.tree.admissible('root'), True)

if __name__ == '__main__':
    unittest.main()