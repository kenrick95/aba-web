import re
from .aba_rule import ABA_Rule
from .aba import ABA

class ABA_Parser():
    def __init__(self, raw):
        self.raw = raw
        self.__regex_rule = re.compile('\s*(?P<symbols>[a-zA-Z0-9 ,]+)?\s*\|-\s*(?P<result>\S+)?\.')
        self.__regex_contrary = re.compile('\s*contrary\(\s*(?P<assumption>\S+)\s*,\s*(?P<symbol>\S+)\s*\)\.')
        
        self.parsed_rules = []
        self.parsed_contraries = dict()
        
    def parse(self):
        errors = []
        
        for matched_rule in self.__regex_rule.finditer(self.raw):
            err = 0
            
            raw_symbols = matched_rule.group('symbols')
            if raw_symbols:
                symbols = [x.strip() for x in raw_symbols.split(',')]
            else:
                symbols = [None]
            result = matched_rule.group('result')
            
            if result and ',' in result:
                errors.append("<%s> result symbol must be atomic." % result)
                err += 1
            
            if err == 0:
                self.parsed_rules.append(ABA_Rule(symbols, result))
            
        
        for matched_rule in self.__regex_contrary.finditer(self.raw):
            err = 0
            
            symbol = matched_rule.group('symbol')
            assumption = matched_rule.group('assumption')
            
            if symbol and ',' in symbol:
                errors.append("<%s> symbol must be atomic." % symbol)
                err += 1
            if assumption and ',' in assumption:
                errors.append("<%s> assumption must be atomic." % assumption)
                err += 1
            
            if err == 0:
                self.parsed_contraries[assumption] = symbol
            
        
        return errors
        
    def __get_aba_symbols(self):
        symbols = set()
        
        for rule in self.parsed_rules:
            symbols.add(rule.result)
            for symbol in rule.symbols:
                symbols.add(rule.result)
        
        return tuple(x for x in iter(symbols))
        
    def construct_aba(self):
        aba = ABA()
        
        aba.symbols = self.__get_aba_symbols()
        
        for rule in self.parsed_rules:
            aba.rules.append(rule)
            
        for assumption, symbol in self.parsed_contraries.items():
            aba.contraries[assumption] = symbol
        
        aba.infer_assumptions()
        
        aba.construct_arguments()
        aba.construct_dispute_trees()
        
        return aba