#!/usr/bin/python
# -*- coding: utf-8 -*-
class ABA_Rule(dict):
    def __init__(self, symbols, result = None):
        dict.__init__(self, symbols = symbols, result = result) # to make it JSON-serializable

        self.symbols = symbols
        self.result = result
    def __str__(self):
        """
        Meaning that set of symbols can derive result
        """
        if None in self.symbols:
            return "|- " + self.result
        return ", ".join(self.symbols) + " |- " + self.result

    def is_ground_truth(self):
        return self.symbols is [None]

    def __eq__(self, other):
        return self.symbols == other.symbols and self.result == other.result
