# TraceContract

## Author: Klaus Havelund 
## Description


TraceContract is an internal DSL (API) in the Scala programming language for
analyzing traces. It allows to write what we refer to as *trace contracts* (expecations of traces).

A trace is a sequence of events, typically produced by a running software 
system. A trace contract is a class that extends the `tracecontract.Monitor` 
class, and specifies which traces are well-formed and which are not. 
The API provides several methods to construct formulas 
in various sub-logics, including temporal logic, 
state machines, code, and liberal combinations thereof.

TraceContract can be used for online monitoring as well as offline monitoring.
However, in the case of online monitoring, the monitored program should preferably be written in a JVM-based programming language, such as Scala or Java.

TraceContract was used daily at NASA Ames Research Center
througout NASA's Lunar LADEE mission to verify
command sequences before they were uploaded to the spacecraft. This application was likely succesful due to the expressiveness of TraceContract, being an extension of a high-level programming language.

## Events

We want to write monitors of communication between a control center and a space craft. First we define an event type ``Event`` defining what events are monitored. Each event type forms a subclass of this type: 

~~~scala
    trait Event
    case class COMMAND(name: String, nr: Int) extends Event
    case class SUCCESS(name: String, nr: Int) extends Event
    case class FAIL(name: String, nr: Int) extends Event
~~~

A trait in scala corresponds to an abstract class in Java (although not quite the same). Each event type is defined as a **case class**. A case class is like a normal class, except e.g. that one can pattern match over case classes, as we shall see. We now assume that a trace is a sequence of events of type ``Event``.

We have here defined three event types: commands that are submitted to the spacecraft, and events reporting whether the commands succeed or fail. Each command instance is identified by a name and a number (commands should be numbered with natural numbers: 0, 1, 2, ...).

## Example 1 - Commands must succeed

The first requirement we define is the following:

> *Whenever a command is observed, a success should follow (with the same
>  command name and number), with no fail before that.* 

This requirement is formulated as follows in TraceContract:

~~~scala
class CommandsMustSucceed extends Monitor[Event] {
  require {
    case COMMAND(name, number) =>
      hot {
        case FAIL(`name`, `number`) => error
        case SUCCESS(`name`, `number`) => ok
      }
  }
}
~~~

The requirement is formulated as a class named ``CommandsMustSucceed`` that extends the ``Monitor`` class instantiated with the ``Event`` type form above.
The method ``require`` takes as argument a Scala partial function, defined with **case** _statements_. The property reads as follows: whenever a 
``COMMAND(name, number)`` occurs, we enter a ``hot``state (a non-acceptance state, it is an error to end up in a hot state). Note that the hot state
is anonymous: it has not name (it is *inlined* so to say). In this state we wait for a ``SUCCESS(`name`, `number`)`` to occur. The quotes around the arguments ``name`` and ``number`` mean that we must match the previously bound values of these variables. However, if a ``FAIL(`name`, `number`)`` event occurs before then an error is reported.

## Example 2 - Commands cannot succeed twice

The second requirement is:

> *A command number cannot succeed more than once.* 

Note that we don't care about the command name.
This requirement is formulated as follows in TraceContract:

~~~scala
class OnlyOneSuccess extends Monitor[Event](Severity.WARNING) {
  require {
    case SUCCESS(_, number) =>
      state {
        case SUCCESS(_, `number`) => error
      }
  }
}
~~~

Note here that the state entered after the first ``SUCCESS(_, number) `` event (wildcard _ means: we ignore this value) is a ``state``, which means an acceptance state (in contrast to a ``hot`` state).

The ``Monitor`` class is instantiated with a ``Severity.WARNING``, which indicates that violating this property is less serious. The default
is ``Severity.ERROR``. These values are in fact objects defining a
``level`` variable. ``Severity.ERROR.level`` has value 10 and ``Severity.WARNING.level`` has value 20. The lower the value the more serious the violation. When properties are violated the violations with the lower values are reported before violations with higher values.

## Example 3 - Commands and successes must alternate

The third requirement is as follows:

> *We should see commands be issued one at a time - each command shall 
> succeed before the next is issued.*

This requirement can be formulated as follows, this time declaring violations
to be of highest importance.

~~~scala
case object SUPERBAD extends Severity {
  val level = 1
}

class Alternation extends Monitor[Event](SUPERBAD) {
  property(S1)

  def S1: Formula =
    weak {
      case COMMAND(name, number) => S2(name, number)
    }

  def S2(name: String, number: Int): Formula =
    weak {
      case SUCCESS(`name`, `number`) => S1
    }
}
~~~

The requirement is defined as a state machine with two states ``S1`` and ``S2``.
Each such state is a ``Formula`` (we have to provide this type for the
program to type check). Each of these two states are defined as ``weak``, which means: the next event has to match one of the transitions, and if not it is an error. However, it is ok if there are no further events. This is in contrast to ``strong`` states, where a next event must occur (similar to *weak next* versus *strong next* in temporal logic).

Observe that state ``S2`` is parameterized with the ``name`` and ``number`` picked up in state ``S1``: the ``SUCCESS`` arguments must match these.

## Example 4 - Double success must be reported

This example illustrates how longer sequences of events can be expressed. Consider the following requirement:

> *If a command is issued, and it subsequently at some later point succeeds,
> and if it succeeds again a second time immediately thereafter in the next
> step, **then** in the immediate subsequent step it must fail*

This requirement can be stated as follows:

~~~scala
class WrongSequence extends Monitor[Event] {
    require {
      case COMMAND(name,number) =>
        state {
          case SUCCESS(`name`,`number`) =>
            step {
              case SUCCESS(`name`,`number`) =>
                strong {
                  case FAIL(`name`,`number`) => ok
                }
            }
        }
    }
}
~~~

The property reads as follows. At any time, in case a ``COMMAND(name,number)``
event is observed, and then some time later a ``SUCCESS(`name`,`number`)``
event is observed, then if in the next step a ``SUCCESS(`name`,`number`)``
occurs, **then** in the next step a ``FAIL(`name`,`number`)`` must occur, and if not an error is reported.

## Example 5 - Numbers must increase by 1

This example illustrates how programming in Scala can be combined with
temporal properties.

Consider the requirement:

> *Consecutive command numbers should increase by exactly 1. In addition, 
> collect the names of the commands issued and print them at the end
> of the trace.* 

This requirement can be stated as follows:

~~~scala
class IncreasingNumbers extends Monitor[Event] {
  var commands: Set[String] = Set()

  require {
    case COMMAND(name, number) =>
      commands += name
      state {
        case COMMAND(_, number2) => number2 == number + 1
      }
  }

  override def finish() {
    println("commands issued: " + commands.mkString(","))
  }
}
~~~

Observe the declaration of the variable ``commands`` (a set of strings) 
to hold the commands observed. It is updated  by adding each command to it.
In addition observe how the target of the last transition is a Boolean
expression ``number2 == number + 1``. This functions as an assertion that this expression must be true, in which case the target state is ``ok``, otherwise it is ``error``. 

The function ``finish`` is predefined in class ``Monitor`` to do nothing. It is called at the end of the trace. Here we override it to print out
the collected command names.

## Explanation of states

We have seen the use of some different states. These are summarized below.
Assume an event ``e`` is observed.

~~~scala 
def state(block: Block): Formula
~~~

A state waiting for an event to possibly match a transition. The first matching event e causes the state to evolve to block(e). The monitor will wait
in this state until such a matching events occurs.

~~~scala
def hot(block: Block): Formula
~~~

Same semantics as a state above, except that it is considered a violation to end in a hot state at the end of the trace analysis. A hot state represents a liveness property: something has to happen eventually.

~~~scala
def strong(block: Block): Formula
~~~

A strong state expects an event to match a transition in the next step. If not, or if there is no next step (at the end of the trace) it evaluates to False (it is an error).

~~~scala
def weak(block: Block): Formula>
~~~

Same semantics as strong, except it is not an error if there is no next step.

~~~scala
def step(block: Block): Formula
~~~

If e matches block then block(e), else True (we simply ignore the rest
of this property). 

## Analyzing a Trace

We can now analyze an execution trace. First we define one monitor that
integrates the five monitors we have seen above. We illustrate that monitors can be combined in a hierachy. In the following we define two monitors
``Properties1`` and ``Properties2``, each of which again contains sub-monitors
that we defined above. Finally, the monitor ``Properties`` combines all 
the monitors.

~~~scala
class Properties1 extends Monitor[Event] {
  monitor(
    new CommandsMustSucceed,
    new OnlyOneSuccess)
}

class Properties2 extends Monitor[Event] {
  monitor(
    new Alternation,
    new WrongSequence,
    new IncreasingNumbers)
}

class Properties extends Monitor[Event] {
  monitor(new Properties1, new Properties2)
}
~~~

The following program applies the ``Properties`` monitor to a trace, which
is here handcrafted:

~~~scala
object TraceAnalysis {
  def main(args: Array[String]) {
    def trace: List[Event] =
      List(
        COMMAND("STOP_DRIVING", 1),       // event #1
        COMMAND("TAKE_PICTURE", 2),       // event #2
        COMMAND("START_DRIVING", 3),      // event #3
        SUCCESS("TAKE_PICTURE", 2),       // event #4
        SUCCESS("STOP_DRIVING", 1),       // event #5
        SUCCESS("TAKE_PICTURE", 2),       // event #6
        COMMAND("STOP_THE_DRIVING", 10),  // event #7
        COMMAND("TAKE_THE_PICTURE", 20),  // event #8
        COMMAND("START_THE_DRIVING", 30), // event #9
        SUCCESS("TAKE_THE_PICTURE", 20),  // event #10
        SUCCESS("STOP_THE_DRIVING", 10),  // event #11
        SUCCESS("TAKE_THE_PICTURE", 20))  // event #12

    val monitor = new Properties
    monitor.verify(trace)
  }
}
~~~

Executing this program results in the following summary to be printed.
Each error is documented with an error trace showing which events
were instrumental in producing the error. The trace causes 8 violations.

~~~
commands issued: TAKE_THE_PICTURE,STOP_DRIVING,START_THE_DRIVING,
TAKE_PICTURE,START_DRIVING,STOP_THE_DRIVING


 _______                  _____            _                  _
|__   __|                / ____|          | |                | |
   | |_ __ __ _  ___ ___| |     ___  _ __ | |_ _ __ __ _  ___| |_
   | | '__/ _` |/ __/ _ \ |    / _ \| '_ \| __| '__/ _` |/ __| __|
   | | | | (_| | (_|  __/ |___| (_) | | | | |_| | | (_| | (__| |_
   |_|_|  \__,_|\___\___|\_____\___/|_| |_|\__|_|  \__,_|\___|\__|

      _____
     |   __|_ _ _____ _____ ___ ___ _ _
     |__   | | |     |     | .'|  _| | |
     |_____|___|_|_|_|_|_|_|__,|_| |_  |
                                   |___|
	
--- Monitor Properties ---

Total number of reports: 8

==================
SEVERITY=SUPERBAD:
==================

Monitor Properties.Properties2.Alternation property violations: 1

------------------------------
Monitor: Properties.Properties2.Alternation
Property violated

Violating event number 2: COMMAND(TAKE_PICTURE,2)
Trace:
  1=COMMAND(STOP_DRIVING,1)
  2=COMMAND(TAKE_PICTURE,2)

------------------------------


===============
SEVERITY=ERROR:
===============

Monitor Properties.Properties1.CommandsMustSucceed property violations: 2

------------------------------
Monitor: Properties.Properties1.CommandsMustSucceed
Property violated due to missing event

Trace:
  3=COMMAND(START_DRIVING,3)

------------------------------
------------------------------
Monitor: Properties.Properties1.CommandsMustSucceed
Property violated due to missing event

Trace:
  9=COMMAND(START_THE_DRIVING,30)

------------------------------

Monitor Properties.Properties2.WrongSequence property violations: 0


Monitor Properties.Properties2.IncreasingNumbers property violations: 3

------------------------------
Monitor: Properties.Properties2.IncreasingNumbers
Property violated

Violating event number 7: COMMAND(STOP_THE_DRIVING,10)
Trace:
  3=COMMAND(START_DRIVING,3)
  7=COMMAND(STOP_THE_DRIVING,10)

------------------------------
------------------------------
Monitor: Properties.Properties2.IncreasingNumbers
Property violated

Violating event number 8: COMMAND(TAKE_THE_PICTURE,20)
Trace:
  7=COMMAND(STOP_THE_DRIVING,10)
  8=COMMAND(TAKE_THE_PICTURE,20)

------------------------------
------------------------------
Monitor: Properties.Properties2.IncreasingNumbers
Property violated

Violating event number 9: COMMAND(START_THE_DRIVING,30)
Trace:
  8=COMMAND(TAKE_THE_PICTURE,20)
  9=COMMAND(START_THE_DRIVING,30)

------------------------------


=================
SEVERITY=WARNING:
=================

Monitor Properties.Properties1.OnlyOneSuccess property violations: 2

------------------------------
Monitor: Properties.Properties1.OnlyOneSuccess
Property violated

Violating event number 6: SUCCESS(TAKE_PICTURE,2)
Trace:
  4=SUCCESS(TAKE_PICTURE,2)
  6=SUCCESS(TAKE_PICTURE,2)

------------------------------
------------------------------
Monitor: Properties.Properties1.OnlyOneSuccess
Property violated

Violating event number 12: SUCCESS(TAKE_THE_PICTURE,20)
Trace:
  10=SUCCESS(TAKE_THE_PICTURE,20)
  12=SUCCESS(TAKE_THE_PICTURE,20)

------------------------------
~~~

## Evaluation of TraceContract

### Pros

* It is highly expresssive, in fact Turing Complete since it is an extension 
of a programming language. This allows TraceContract to be used in realistic scenarios where often advanced forms of computations are needed, such as string manipulations and number calculations. Scala itself is a high-level
object-oriented and functional programming language, resulting in a very
convenient modeling language.

* It is reasonably elegant to write properties in. Using TraceContract is often a fun experience.

* Since it is an API in a programming language, a programmer trained in that programming language can relatively easlily adopt it and be up and running fast.

### Cons

* Since it is an API in a programming language, a user has to be a (Scala) programmer, which limits the applicability. Had it been e.g. Python this might have been less of a problem.

* The DSL is a so-called *shallow DSL*, which means that Scala's language constructs are part of the DSL (in contrast a *deep DSL* where one creates an entire Abstract Syntax for the DSL in Scala). This means that it is not possible to easily analyze TraceContract programs and optimize them for speed and memory consumption. 

* The DSL is probably not as slick as it could be as if it was designed all from scratch without being an extension of a programming language. 

## References & links

* URL: https://github.com/havelund/tracecontract
* [*TraceContract: A Scala DSL for Trace Analysis*](tracecontract-fm-2011.pdf) Howard Barringer and Klaus Havelund, FM'11, Lecture Notes in Computer Science, vol. 6664, 2011. 

## Classification

* Use Table 5 from the STTT-paper (https://link.springer.com/article/10.1007%2Fs10009-017-0454-5) to self-categorize tool.

|U.spec|B.spec|Prop|Par|Aut|Log|Reg|Ord|Time|Ins|AJ |C  |Java|Tra|T.trig|E.trig|
|:-----:|:---:|:--:|:-:|:-:|:-:|:-:|:-:|:--:|:-:|:-:|:-:|:--:|:-:|:----:|:----:|
| x     |     | x  | x | x | x |   | x |(x)|   | x |   |  x | x |      |   x  |

* U.spec = User-enabled
* B.spec = Built-in 
* Prop = Propositional events
* Par = Parametric events
* Aut = Automata-based
* Log = Logic-based
* Reg = Regular Expressions-based
* Ord = Logical-time
* Time = Real-time
* Ins = Own instrumentation
* AJ = Relies on AspectJ
* C  = C programs
* Java = Java programs
* Tra = Traces
* T.trig = Time triggered 
* E.trig = Event triggered
