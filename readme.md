# Web-based Argumentation
Test status: [![CircleCI](https://circleci.com/gh/kenrick95/aba-web/tree/master.svg?style=svg&circle-token=3eee74022841f7537e825b583d3459b0ef10df4d)](https://circleci.com/gh/kenrick95/aba-web/tree/master)

- Assumption-based Argumentation
- Interface to web
- input: argumentation rules
- output: which argument is complete, grounded, admissible; with some visualization if possible

## Architecture
- Static page served by Python Flask web-framework
- Input parsed by Parser
- Parser attempts to construct the ABA Framework, including
    - ABA Arguments
    - ABA Dispute Trees
- Outputs the visualization of the arguments and dispute trees, including
    - semantics, elaborated in subsequent section

### Parser

```
a, b, c |- d.
```

Rule
- LHS contains zero or more space-separated symbols
- RHS conrains exactly one symbol

Meaning
- Symbols in LHS supports the RHS symbol, making a potential argument
- If LHS is empty, then the potential argument is a ground truth
- If the symbols contained in LHS are ground truths or assumptions or both, then the potential argument is an actual argument

Notes
- If the sentence is potential argument, it will not be used in the dispute tree derivation

```
contrary(a, b).
```
Rule
- a function containing two parameters, both accepting a symbol

Meaning
- first symbol is a contrary of second symbol
- first symbol is an assumption

```
assumption(x).
```
Rule
- a function containing one parameter accepting a symbol

Meaning
- explicitly state the parameter is an assumption

### Argument semantics implemented
- Conflict-free
- Admissible
- Complete
- Grounded
- Stable
- Ideal

### Testing
Using Python unittest framework, tests mainly sourced from examples presented at Craven, Toni "Argument Graphs and Assumption-Based Argumentation" (2016).

## Notes

This work is based mainly on the paper Dung, Kowalski, Toni titled "Assumption-based Argumentation" (2009).

`requirements.txt` contains libraries needed for setting up the project.

The following files are related to deployment in Microsoft Azure, please disregard them when evaluating the project:

- `ptvs_virtualenv_proxy.py`
- `runtime.txt`
- `web.config`
- `wheelhouse/ujson-1.35-cp34-none-win32`
