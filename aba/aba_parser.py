import re
from aba_rule import ABA_Rule

class ABA_Parser():
    def __init__(self, raw):
        self.raw = raw
        self.__regex = re.compile('\s*(?P<symbols>.*\S)?\s*\|-\s*(?P<result>\S+)?\n')
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