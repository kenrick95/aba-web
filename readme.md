# Web-based Argumentation
Test status: [![CircleCI](https://circleci.com/gh/kenrick95/aba-web/tree/master.svg?style=svg&circle-token=3eee74022841f7537e825b583d3459b0ef10df4d)](https://circleci.com/gh/kenrick95/aba-web/tree/master)

Extra short summary of this project:

- Assumption-based Argumentation solver
- Plus a web interface
- Input: argumentation rules
- Output: which argument is conflict-free, stable, complete, admissible, ideal, grounded.
- FYP report: [link](https://github.com/kenrick95/aba-web/files/585224/Amended-report-Kenrick-2016-11-11.pdf).

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

This work is based mainly on the book chapter authored by Dung, Kowalski, Toni titled ["Assumption-based Argumentation"](http://www.doc.ic.ac.uk/~rak/papers/ABAfinal.pdf) (2009).

`requirements.txt` contains libraries needed for setting up the project.

The following files are related to deployment in Microsoft Azure, please disregard them when evaluating the project:

- `ptvs_virtualenv_proxy.py`
- `runtime.txt`
- `web.config`
- `wheelhouse/ujson-1.35-cp34-none-win32`

## Performance Testing
- `perf_memory_limitter.py` is for limitting RAM usage, returning MemoryError if Python overshoot a certain amount of RAM usage
- `perf_test.py` is the main file to test performance of this project.
- `perf_test_runonly.txt` is the list of test cases used in `perf_test.py`
- `pert_test_proxdd.py` is a wrapper to test the performance of [*proxdd*](http://robertcraven.org/proarg/proxdd.html), a Prolog program by Toni (2012).
- `perf_test_proxdd_setup.txt` is the list of test cases used in `pert_test_proxdd.py`, essentially the same as `perf_test_runonly.txt`
