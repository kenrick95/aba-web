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
        
    def __process_parse_rule(self, rule_match):
        errors = []
        raw_symbols = rule_match[0]
        result = rule_match[1]
        
        if raw_symbols:
            symbols = [x.strip() for x in raw_symbols.split(',')]
        else:
            symbols = [None]
        
        if result and ',' in result:
            errors.append("result symbol <%s> must be atomic." % result)
        
        if len(errors) == 0:
            self.parsed_rules.append(ABA_Rule(symbols, result))
        
        return errors
        
    def __process_parse_contrary(self, contary_match):
        errors = []
        print(contary_match)
            
        assumption = contary_match[0]
        symbol = contary_match[1]
        
        if symbol and ',' in symbol:
            errors.append("symbol <%s> must be atomic." % symbol)
        if assumption and ',' in assumption:
            errors.append("assumption <%s> must be atomic." % assumption)
        
        if len(errors) == 0:
            self.parsed_contraries[assumption] = symbol

        return errors

    def parse(self):
        errors = []
        
        for i, raw_line in enumerate(self.raw.splitlines()):
            line = raw_line.strip()
            
            if len(line) == 0: # after stripping spaces, nothing left
                continue
            
            line_errors = []
            rule_matches = self.__regex_rule.findall(line)
            contrary_matches = self.__regex_contrary.findall(line)
            
            if len(rule_matches) + len(contrary_matches) == 0: # no match
                line_errors.append("Error: Line %d is neither a rule nor contrary: %s" % (i, line))
            elif len(rule_matches) * len(contrary_matches) > 0: # match more than one type
                line_errors.append("Error: Line %d should not contain both rule and contrary: %s" % (i, line))
            elif len(rule_matches) + len(contrary_matches) > 1:  # match more than one in a line
                line_errors.append("Error: Line %d should not contain more than one rule or contrary: %s" % (i, line))
            
            if len(line_errors) > 0:
                errors.extend(line_errors)
                continue
            
            
            if len(rule_matches) == 1:
                process_errors = self.__process_parse_rule(rule_matches[0])
                line_errors.extend(["Error: Line %d %s" %(i, x) for x in process_errors])
                
            elif len(contrary_matches) == 1:
                process_errors = self.__process_parse_contrary(contrary_matches[0])
                line_errors.extend(["Error: Line %d %s" %(i, x) for x in process_errors])
            
            errors.extend(line_errors)
            
            
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