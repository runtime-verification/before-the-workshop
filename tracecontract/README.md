# RV Challenge & Cheat Sheet

## Tool and Spec language: TraceContract
## Author: Klaus Havelund 
## Description


TraceContract is an internal DSL (API) in the Scala programming language for
analyzing traces. It allows to write what we refer to as trace contracts (expecations of traces).

A trace is a sequence of events, typically produced by a running software 
system. A trace contract is a class that extends the `tracecontract.Monitor` 
class, and specifies which traces are well-formed and which are not. 
A trace contract consists of one or more properties, where a property is 
a named formula. The API provides several methods to construct formulas 
in various sub-logics, including LTL (Linear Temporal Logic), 
state machines, rule-based systems, and liberal combinations thereof.

* My favourite specification (or two)
* A short paragraph explaining the property
* What is your formalism good at/what is missing? Application area?

## Evaluation of TraceContract

### Pros

* It is highly expresssive, in fact Turing Complete since it is an extension 
of a programming language. This allows TraceContract to be used in realistic scenarios where often advanced forms of computations are needed, such as string manipulations and number calculations.

* Since it is an API in a programming language, a (Scala) programmer can relatively easlily adopt it and be up and running fast.

### Cons

* Since it is an API in a programming language, a user has to be a (Scala) programmer, which limits the applicability. Had it been Python this might have been less of a problem.

* The DSL is a so-called shallow DSL, which means that Scala's language constructs are part of the DSL (in contrast to creating an entire Abstract Syntax for the DSL in Scala). This means that there are limits to how easy
 it is to add new constructs. E.g. TraceContract is not good at past time temporal properties (although a newer version has been created that to some extent tries to solve this problem). Also, it is not possible to easily analyze TraceContract programs and optimize them for speed and memory consumption.

## References & links

* URL: https://github.com/havelund/tracecontract


## Classification

* Use table from the STTT-paper (https://link.springer.com/article/10.1007%2Fs10009-017-0454-5) to self-categorize tool here in the template.

