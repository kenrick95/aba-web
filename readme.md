Web-based Argumentation
Assumption-based Argumentation
Interface to web
input: argumentation rules
output: which argument is complete, grounded, admissible; with some visualization if possible

## Architecture
- Static page served by Python Tornado web-framework/server
- Input parsed by Parser
- Parser output processed by ABAModel
- ABAModel tells server about its properties
- Done?

- Misc: testing

### Parser
- Prolog-like
- might be very difficult
- especially recursive functions

### Testing
- Python unittest framework

