import re
from .aba_rule import ABA_Rule
from .aba import ABA

class ABA_Parser():
    def __init__(self, raw):
        self.raw = raw
        self.__regex_rule = re.compile(r'\s*(?P<symbols>[a-zA-Z0-9 ,]+)?\s*\|-\s*(?P<result>\S+)?\.')
        self.__regex_contrary = re.compile(r'\s*contrary\(\s*(?P<assumption>\S+)\s*,\s*(?P<symbol>\S+)\s*\)\.')
        self.__regex_assumption = re.compile(r'\s*assumption\(\s*(?P<assumption>\S+)\s*\)\.')
        
        self.parsed_rules = []
        self.parsed_contraries = dict()
        self.parsed_assumptions = []
        
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

        assumption = contary_match[0]
        symbol = contary_match[1]
        
        if symbol and ',' in symbol:
            errors.append("symbol <%s> must be atomic." % symbol)
        if assumption and ',' in assumption:
            errors.append("assumption <%s> must be atomic." % assumption)
        
        if len(errors) == 0:
            self.parsed_contraries[assumption] = symbol

        return errors

    def __process_parse_assumption(self, assumption_match):
        errors = []
        
        assumption = assumption_match
        
        if assumption and ',' in assumption:
            errors.append("assumption <%s> must be atomic." % assumption)
        if assumption in self.parsed_assumptions:
            errors.append("assumption <%s> has already existed on another statement" % assumption)
        
        if len(errors) == 0:
            self.parsed_assumptions.append(assumption)

        return errors

    def parse(self):
        errors = []
        
        for j, raw_line in enumerate(self.raw.splitlines()):
            line = raw_line.strip()
            i = j + 1
            
            if len(line) == 0: # after stripping spaces, nothing left
                continue
            
            line_errors = []
            rule_matches = self.__regex_rule.findall(line)
            contrary_matches = self.__regex_contrary.findall(line)
            assumption_matches = self.__regex_assumption.findall(line)

            error_types = (len(rule_matches) > 0) ^ (len(contrary_matches) > 0) ^ (len(assumption_matches) > 0)
            
            if error_types == 0: # no match
                line_errors.append("Error: Line %d is neither a rule, a contrary, nor an assumption: %s" % (i, line))
            elif error_types > 1: # match more than one type
                line_errors.append("Error: Line %d should not contain more than one type of statements: %s" % (i, line))
            elif len(rule_matches) + len(contrary_matches) + len(assumption_matches) > 1:  # match more than one in a line
                line_errors.append("Error: Line %d should not contain more than one statements: %s" % (i, line))
            
            if len(line_errors) > 0:
                errors.extend(line_errors)
                continue
            
            
            if len(rule_matches) == 1:
                process_errors = self.__process_parse_rule(rule_matches[0])
                line_errors.extend(["Error: Line %d %s" %(i, x) for x in process_errors])
                
            elif len(contrary_matches) == 1:
                process_errors = self.__process_parse_contrary(contrary_matches[0])
                line_errors.extend(["Error: Line %d %s" %(i, x) for x in process_errors])

            elif len(assumption_matches) == 1:
                process_errors = self.__process_parse_assumption(assumption_matches[0])
                line_errors.extend(["Error: Line %d %s" %(i, x) for x in process_errors])
            
            errors.extend(line_errors)
            
            
        return errors
        
    def __get_aba_symbols(self):
        symbols = set()
        
        for rule in self.parsed_rules:
            symbols.add(rule.result)
            for symbol in rule.symbols:
                if symbol is not None:
                    symbols.add(symbol)

        for assumption in self.parsed_assumptions:
            if assumption is not None:
                symbols.add(assumption)
        
        return tuple(x for x in iter(symbols))
        
    def construct_aba(self):
        aba = ABA()
        
        aba.symbols = list(self.__get_aba_symbols())
        
        for rule in self.parsed_rules:
            aba.rules.append(rule)
            
        for assumption, symbol in self.parsed_contraries.items():
            aba.contraries[assumption] = symbol

        for assumption in self.parsed_assumptions:
            aba.assumptions.append(assumption)
        
        aba.infer_assumptions()
        
        aba.construct_arguments()
        aba.construct_dispute_trees()
        
        return aba