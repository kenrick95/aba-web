class ABA_Rule(dict):
    def __init__(self, symbols, result = None):
        dict.__init__(self, symbols = symbols, result = result) # to make it JSON-serializable
        
        self.symbols = symbols
        self.result = result
    def __str__(self):
        """
        Meaning that set of symbols can derive result
        """
        return self.symbols + " |- " + self.result
    
    def is_assumption(self):
        return self.result is None
        
    def is_ground_truth(self):
        return self.symbols is [None]