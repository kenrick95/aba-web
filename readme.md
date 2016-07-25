# Web-based Argumentation

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


### Testing
- Python unittest framework


## Argument semantics
- Conflict-free
- Admissible
- Complete
- Grounded
- Stable
- Ideal

### TODO
- preffered

## Some other notes
This work is based on the paper Dung, Kowalski, Toni titled "Assumption-based Argumentation".


Complete if and only if it is admissible and contains all arguments it can defend (by attacking all arguments attacking them)


(Abstract argumentation)
Definition 2.2. A set X of arguments is
• admissible iff X does not attack itself and X attacks every set of arguments Y such that Y attacks X;
• preferred iff X is maximally admissible;
• complete iff X is admissible and X contains all arguments x such that X attacks all attacks against x;
• grounded iff X is minimally complete;
• ideal iff X is admissible and it is contained in every preferred set of arguments.

(TODO: Improve efficiency)
Computationally, the use of assumption-based argumentation allows to exploit the fact that different arguments can
share the same assumptions and thus avoid recomputation in many cases and the need to worry about sub-arguments
of arguments.


Notation 2.1. In the remainder of this paper, we denote an argument for a conclusion α supported by a set of assumptions
A simply as A |- α.
Given an argument a of the form A |- α we say that α is based upon A.


Theorem 3.3. An admissible set of arguments S is ideal iff for each argument 'a' attacking S there exists no admissible
set of arguments containing 'a' 

Definition 3.3. An admissible dispute tree T is ideal if and only if for no opponent node O in T there exists an
admissible tree with root O..



an admissible set of arguments is complete if it contains all arguments that it
defends, where a set of arguments Arg defends an argument arg if Arg attacks all
arguments that attack {arg};

--> complete iff it is admissible and contains all arguments it can defend(by attacking all arguments attacking them);

https://en.wikipedia.org/wiki/Argumentation_framework
Stable:  iff the set of assumptions does not attack itself [conflict-free] and it attacks every assumption not in the set.
Preferred: A set of assumptions is a preferred argument iff it is a maximal (with respect to set inclusion) admissible argument. ???


http://math.stackexchange.com/questions/1034014/how-are-inclusion-wise-maximal-and-minimal-sets-defined
An inclusion-wise maximal set among a collection of sets is a set that is not a subset of some other set in the collection. An inclusion-wise minimal set among a collection of sets is a set in the collection that is not a superset of any other set in the collection.

http://www.sciencedirect.com/science/article/pii/000437029400041X
> A preferred extension of an argumentation framework (AF) is a maximal (w.r.t. set inclusion) admissible set of AF.

http://logcom.oxfordjournals.org.ezlibproxy1.ntu.edu.sg/content/13/3/377.short 
