# Modbat, a model-based tester

## Modbat's DSL
## Author(s): Cyrille Artho
## Description

Modbat is a model-based testing tool that is based on annotated (extended)
finite-state machines.

Modbat is specialized to testing the application programming interface
(API) of software. The model used by Modbat is compatible with Java
bytecode. The user defines and compiles a model, which is then explored
by Modbat and executed against the system under test. Failed test runs
are reported as an error trace.

Modbat is based on Scala and compatible with any Java-based software. The
model has the structure of a non-deterministic finite-state machine. From
all possible transitions, one is chosen to be tested; annotations of
the transition specify which code to execute.

The tool is run from the command line; details (including the tool itself,
source code, and a video) are available from the
[Modbat home page](https://people.kth.se/~artho/modbat/).

Modbat has been designed to make it easy to model state-based APIs where
some calls may throw exceptions. The occurrence of exceptions may be
impossible to predict in all cases, such as when network I/O is used.
In contrast to ScalaCheck, which is weak in these areas, Modbat does not
have any elaborate mechanism to generate diverse input data. Indeed,
the design decision is to combine data generators from ScalaCheck for
such cases.

## References & links

* [Main page](https://people.kth.se/~artho/modbat/)
* [Tool demo](https://people.kth.se/~artho/modbat/tooldemo/)

## A simple example: SimpleListModel

This model tries a few random operations on a linked list, and checks
in transition "size" if the size corresponds to the expected size.
This model uses one state but keeps track of the size of the list using
a variable.

More elaborate models include the use of (multiple) iterators and
other operations on the list; see [Tool
demo](https://people.kth.se/~artho/modbat/tooldemo/).

~~~scala
import java.util.LinkedList
import java.util.Iterator
import modbat.dsl._

class SimpleListModel extends Model {
  val N = 10 // range of integers to choose from
  val collection = new LinkedList[Integer] // the "system under test"
  var n = 0 //Number of element in the collection

  def add {
    val element = new Integer(choose(0, N))
    val ret = collection.add(element)   
    n += 1
    assert(ret)
  }

  def clear {
    collection.clear
    n = 0
  }

  def remove {
    val obj = new Integer(choose(0, N))
    val res = collection.remove(obj)
    n = n - 1
  }

  def size {
    assert (collection.size == n, "Predicted size: " + n + ", actual size: " + collection.size)
  }

  "main" -> "main" := add
  "main" -> "main" := size
  "main" -> "main" := clear
  "main" -> "main" := remove
}
~~~
