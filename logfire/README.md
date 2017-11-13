# LogFire

## Author: Klaus Havelund 
## Description


LogFire is an internal DSL (API) in the Scala programming language for
analyzing traces. A trace is a sequence of events, typically produced by a running software 
system. LogFire is based on a view that a monitor is a rule-based program consisting of a collection of named rules (names are strings). A rule has the form: 

    name : c1 & c2 & ... & cn |-> a
    
with a left-hand side (to the left of ``|->``) consising of a sequence of conditions, and the right-hand side  (to the right of ``|->``) consisiting of an action. A rule fires if the conditions all evaluate to true, in which case the action is executed. Rules work on a database of *facts*. A fact is a named data record. Conditions can check the precense or absence of facts and the action can add or delete facts. Since LogFire is an internal Scala DSL, actions can in general execute any Scala code.

LogFire can be used for online monitoring as well as offline monitoring.
However, in the case of online monitoring, the monitored program should preferably be written in a JVM-based programming language, such as Scala or Java.

LogFire is implemented as a modification of the Rete algorithm, which for a long time has been
used by the rule-based AI community, as e.g. implemented in Drools and CLIPS. It has in LogFire been modified treat events in a special manner for monitoring, making them short-lived: when submitting an event to a monitor it only survives in one step, enough to evaluate the left-hand sides of active rules. The Rete algorithm is rather complex and minimizes the evaluation of rule left-hand sides when a new event arrives.

LogFire has been used daily during for analyzing telemetry coming down from the Curiosity rover on Mars. However, that use only had actions that were pure Scala code. Hence no creation of facts for the database. It is therefore a limited use of this tool not really using it as it was intended. 

## The Command Execution Study

We want to write monitors of communication between a control center and a space craft. 
A trace is considered as a sequence of events, where an individual event is a mapping from symbols to values. That is, an event has the type:

~~~scala
Map[Symbol, Any]
~~~

In Scala type ``Symbol`` contains quoted names, such as ``'time`` (symbols are easier to type than strings).
For example, the following is an event:

~~~scala
Map('command -> "DRIVE", 'time -> 267833)
~~~

Events can (but do not need to) have a kind, indicated by a the symbol 'kind mapping to a symbol, as in:

~~~scala
Map('kind -> 'EVR, 'command -> "DRIVE", 'time -> 267833)
~~~

Such events can (but do not need to) be written in the special format:

~~~scala
'EVR('command -> "DRIVE", 'time -> 267833)
~~~

Use of Scala's implicit function definitions under the hood will make all this work. As we shall see, events can also be provided in positional format:

~~~scala
'EVR("DRIVE",267833)
~~~

This has the same meaning as the following map-constructing expression:

~~~
Map('kind -> 'EVR, 'one -> "DRIVE", 'two -> 267833)
~~~

Facts are in essence of the same format as events. They are created during monitoring as rules match and rule right-hand sides are executed. In contrast to events, however, a fact survives in the fact memory until it is removed again explicitly by a rule right-hand side action.


## Some Properties

Below is a list of properties we want to hold over traces of such events.

- **P1.**  *An issued command should eventually succeed without failing first.*
- **P2.** *A command cannot succeed more than once.*
- **P3.** *A non-issued command cannot succeed.*

Note that a "liveness" property such as **P1** only makes sense for finite traces. However,
log files are finite traces and form an important application of runtime verification.

## Formalized in LogFire

We now formalize the above properties in LogFire. They are all formulated as one monitor. 

~~~scala
class CommandMonitor1 extends Monitor {
  val COMMAND, SUCCESS, FAIL, END = event
  val Commanded, Succeeded = fact

  "record command" --
    COMMAND('name, 'number) |-> insert(Commanded('name, 'number))

  "record success" --
    Commanded('n, 'x) & SUCCESS('n, 'x) |-> replace(Commanded)(Succeeded('n, 'x))

  "record failure" --
    Commanded('n, 'x) & FAIL('n, 'x) |-> {
      remove(Commanded)
      fail(s"command (${'n.s},${'x.i}) failed before success")
    }

  "double succcess" --
    Succeeded('n, 'x) & SUCCESS('n, 'x) |-> fail(s"two successes of (${'n.s},${'x.i}})")

  "success of non-issed command" --
    SUCCESS('n, 'x) & not(Commanded('n, 'x)) |-> 
      fail(s"success of non-issued command (${'n.s},${'x.i}})")

  "catch non-succeeded commands" --
    END() & Commanded('n, 'x) |-> {fail(s"command (${'n.s},${'x.i}}) never succeeded")}
}
~~~

The monitor is a class extending the ``Monitor`` class, which defines all the LogFire DSL features. The first two lines declares the events observed (submitted to the monitor) and the facts that the monitor creates to perform the monitoring. The monitor contains six rules.
These can be read as follows:

- "record command": when a command is obseved, create a ``Commanded`` fact in the database.
- "record success": when a command succeeds, and it has been commanded in the past, replace the
``Commanded`` fact with a ``Succeeded`` fact.
- "record failure": When a commanded commmand fails, remove the ``Commanded`` fact and report the failure.
- "double succcess": When a command succeeds that succeeded in the past, report this.
- "success of non-issed command": When a non-commanded command succeeds, report this.
- "catch non-succeeded commands": At the end, report eny ``Commanded`` facts that have not been resolved by a success of that command.

The same properties can be formalized using map-like events where arguments to events are refered to by name. This can be useful in case of events carrying many arguments.

## Analyzing a Trace

We can now analyze an execution trace. The following program applies the monitor to a trace, which is here handcrafted:

~~~scala
object Test1 {
  def main(args: Array[String]) {
    val m = new CommandMonitor1
    m.addEvent('COMMAND)("STOP_DRIVING", 1)
    m.addEvent('COMMAND)("START_CAMERA", 2)
    m.addEvent('COMMAND)("TURN_ANTENNA", 3)
    m.addEvent('FAIL)("STOP_DRIVING", 1)
    m.addEvent('SUCCESS)("START_CAMERA", 2)
    m.addEvent('SUCCESS)("START_CAMERA", 2)
    m.addEvent('SUCCESS)("START_DRIVING", 4)
    m.addEvent('END)()
  }
}
~~~

Error messages will be printed on standard out as violations are detected. The results can
also be accessed through the API. Error messages include an error trace indicating what events contributed to the problem.


### Programming Templates

One can program abbreviations for rule programs. We shall e.g. want to program the following three
templates:

~~~scala
"r1" --- a --> b      // event a should be followed eventually by event b
"r2" --- a -| c |-> b // when observing event a there should be no c event unless after the next b
"r3" --- a <-- b      // event b should be preceeded in the past by event a
~~~

The following ``Observer`` class implements these three operators using Scala's tricks
for implementaing internals DSLs (we shall not here provide an explanation of this class, the
reader is referred to the journal article referenced at the bottom of this page):

~~~scala
class Observer extends Monitor {
  def absence(name: String)(a: Cond, b: Cond, c: Cond) {
    val a_seen_sym = newSymbol()
    val a_seen = a_seen_sym(a.getVariables: _*)
    "a" -- a |-> a_seen
    "b" -- b & a_seen |-> fail(s"$name - ${eval(a)} and then ${eval(b)} before ${eval(c)}")
    "c" -- c & a_seen |-> remove(a_seen_sym)
  }

  def presence(name: String)(a: Cond, b: Cond) {
    val a_seen_sym = newSymbol()
    val a_seen = a_seen_sym(a.getVariables: _*)
    "a" -- a |-> a_seen
    "b" -- b & not(a_seen) |-> fail(s"not ${eval(a)} before ${eval(b)}")
  }

  implicit def absence_syntax(name: String) = new {
    implicit def ---(a: Cond) = new {
      def -|(b: Cond) = new {
        def |->(c: Cond) {
          absence(name)(a, b, c)
        }
      }

      def -->(b: Cond) {
        absence(name)(a, 'END(), b)
      }

      def <--(b: Cond) {
        presence(name)(a, b)
      }
    }
  }
}
~~~

With this definition, one can define the following monitor:

~~~scala
class CommandMonitor2 extends Observer {
  "commands must succeed" ---
    'COMMAND('x, 'y) --> 'SUCCESS('x, 'y)

  "commands must not fail before success" ---
    'COMMAND('x, 'y) -| 'FAIL('x, 'y) |-> 'SUCCESS('x, 'y)

  "commands cannot succeed without having been issued" ---
    'COMMAND('x, 'y) <-- 'SUCCESS('x, 'y)
}
~~~

## Evaluation of LogFire

### Pros

* It is highly expresssive, in fact Turing Complete since it is an extension 
of a programming language. This allows LogFire to be used in realistic scenarios where often advanced forms of computations are needed, such as string manipulations and number calculations. Scala itself is a high-level object-oriented and functional programming language, resulting in a very convenient modeling language.

* Ignoring Scala, rule-based programming is quite powerful.

* Since it is an API in a programming language, a programmer trained in that programming language can relatively easlily adopt it and be up and running fast.

### Cons

* Since it is an API in a programming language, a user has to be a (Scala) programmer, which limits the applicability. Had it been e.g. Python this might have been less of a problem.

* Rule-based programs are rather verbose and low-level, somewhat similar to writing state machines.

* The DSL is in part an external DSL (the rule left-hand sides) and in part an internal DSL (the right-hand sides can be any Scala code). Concerning the rule left-hand sides, there is no type checking performed, and one has to use quoted names for variables (slightly annoying). The DSL therefore feels a little unsafe.

## References & links

* URL: [https://github.com/havelund/logfire](https://github.com/havelund/logfire)
* [*Rule-based Runtime Verification Revisited*](sttt-2013-logfire.pdf) Klaus Havelund, International Journal on Software Tools for Technology Transfer (STTT), volume 17, issue 2, page 143-170. Published online April 2013. Paper version March 2015. 

