# DejaVu

## Author: Klaus Havelund, Doron Peled, Dogan Ulus
## Description


DejaVu is a newly developed tool for monitoring past first order temporal logic (i.e., first
order safety properties). It was developed by Klaus Havelund (NASA/JPL), Doron Peled (Bar Ilan)
and Dogan Ulus (Verimag). It is based on BDD representation. The values appearing
in the input are enumerated, and the BDD represents the relationship between the data
values, according to their appearance in the monitored sequence and the tested temporal
formula. It allows the use of infinite domains of values, by encoding a special value for "all the
rest of values not seen", whose relationship to other values is maintained during the monitoring.
The BDD can be expanded dynamically when more space is needed. Initial experiments show
very efficient behavior. 


## Evaluation of Dejavu

### Pros

* BDDs seem for efficiency reasons a promising representation of data observed in a trace. It is, however, currently not clear how well they perform compared to slicing, which is considered very fast.

* Properties are very elegant to express.

* The logic is expressive in that arbitrary alternations of universal and existential quantification is allowed.

### Cons

* Due to the fact that data in the trace are mapped to BDDs, it becomes non-obvious how to interpret data operations on formulas. For example it is non-trivial to compare data values beyond equality and it becomes non-trivial to apply functions to observed data values to obtain new values. However, the slicing approaches, such as found in MOP e.g., seem to suffer from the same limitations.

## References & links

* URL: [https://github.com/havelund/tracecontract/tree/master/dejavu](https://github.com/havelund/tracecontract/tree/master/dejavu)
* [*First Order Temporal Logic Monitoring with BDDs*](fmcad-2017.pdf), Klaus Havelund, Doron Peled, and Dogan Ulus,  17th Conference on Formal Methods in Computer-Aided Design (FMCAD 2017), 2-6 October, 2017, Vienna, Austria. IEEE, 2017, pp. 116-123.  


