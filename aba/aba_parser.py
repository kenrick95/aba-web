import re
from .aba_rule import ABA_Rule
from .aba import ABA

class ABA_Parser():
    def __init__(self, raw):
        self.raw = raw
        self.__regex = re.compile('\s*(?P<symbols>.*\S)?\s*\|-\s*(?P<result>\S+)?\.')
        # TODO: handle ground truth
        # TODO: add syntax for defining contraries
        self.parsed_rules = []
        
    def parse(self):
        errors = []
        
        for matched_rule in self.__regex.finditer(self.raw):
            err = 0
            
            raw_symbols = matched_rule.group('symbols')
            symbols = [x.strip() for x in raw_symbols.split(',')]
            result = matched_rule.group('result')
            if result and ',' in result:
                errors.append("<%s> result symbol must be atomic." % result)
                err += 1
            
            if err == 0:
                self.parsed_rules.append(ABA_Rule(symbols, result))
            
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
        
        aba.infer_assumptions()
        
        aba.construct_arguments()
        
        return aba