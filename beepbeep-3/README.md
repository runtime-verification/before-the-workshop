BeepBeep 3
==========

## Author

- Sylvain Hallé (shalle@acm.org)

## Description

BeepBeep is an event stream processing engine. In BeepBeep, streams of events
(of any kind) are piped into computing units called *processors*. The output of
processors can be used as the input of other processors, forming potentially
complex *processor chains*.

## Creating processor chains

A first way of creating processor chains is programmatically. BeepBeep can be
used as a Java library that provides objects for creating, connecting and
running `Processor` objects.

### Example 1: cumulative average

This first query reads from two sources of numbers: a source of arbitrary
values, and a source of "ones". It computes the cumulative sum of both, and
divides the first resulting stream by the other. The end result is an output
stream that represents the *cumulative average* of all values in the first
input stream.

![Processor chain](Average.png?raw=true)

See the [Java code](https://liflab.github.io/beepbeep-3-examples/classbasic_1_1_average.html)
that builds this processor chain.

### Example 2: keep only even numbers

The second example shows that BeepBeep processors do not necessarily output
one event for each input event. Here, a `Filter` processor (traffic light)
receives two streams: the first is a stream of numbers, and the second is a
stream of Booleans. These Booleans are themselves obtained by evaluating if
the incoming number is *both* an even number, and greater than 4.

![Processor chain](FilterConditionComposite.png?raw=true)

Here, the filter outputs either the event from its top stream, if it is even
and greater than 4, or nothing at all, otherwise. This example also shows the
use of colors to designate event streams of various types. For example, in all
the queries, dark green represents numbers.

See the [Java code](https://liflab.github.io/beepbeep-3-examples/classbasic_1_1_filter_condition_composite.html)
that builds this processor chain.

### Example 3: smoothed average over values of a JSlider

BeepBeep's event sources can be anything. In this example, a stream of numbers
is built by polling the value of a slider in a JFrame twice per second. This
stream is used to display a plot with two data series: the raw values and the
smoothed values over a sliding window of 4 events.

![Processor chain](AverageSlider.png?raw=true)

See the [Java code](https://liflab.github.io/beepbeep-3-examples/classwidgets_1_1_average_slider.html)
that builds this processor chain.

### Example 4: statistics

This processor chain takes a stream of numerical values, and raises an alarm
when two successive values are more than one standard deviation away from the
cumulative average of all values seen so far.

![Processor chain](StatQuery.png?raw=true)

The alarm is materialized by the output stream, which returns *true* when the
second of the two "faulty" input events is received (it returns false the rest
of the time).

### Example 5: XPath and logical operators

This query corresponds to the
[*Turn Around* property](http://crv.liflab.ca/wiki/index.php/Offline_Team1_Benchmark3)
of the Pingus benchmark at the CRV 2016. All details regarding this example can be
found in the paper
[Automated Bug Finding in Video Games: A Case Study for Runtime Monitoring](https://www.researchgate.net/publication/261552625).
We highly recommend you scan that paper first.

In a nutshell, a video game generates a stream of XML events about the
x-y position and velocity of about 50 independent characters, called *Pingus*,
moving around on a game field. The property "Turn Around" stipulates that
every time a "walker" Pingu encounters a "blocker" Pingu, it must turn around
and continue walking in the opposite direction.

![Processor chain](Pingus.png?raw=true)

This property is complexified by two details relative to the implementation
of the game. First, the collision is not pixel-perfect: an "encounter" between
two Pingus at positions (x₁,y₁) and (x₂,y₂) occurs whenever:

|x₁-x₂| < 6 and |y₁-y₂| < 10

Second, the "turn around" part does not occur immediately. It may take up to
three cycles of the game loop before the Pingu actually turns.

### Example 6: Moore Machines and parametric trace slicing


### Example 7: signal processing



### Example 8: distribution of computation

One of BeepBeep's palettes allows data to be transmitted over the network
through HTTP requests. On Machine A (top), numbers are summed, packed into list
every second, serialized into JSON and sent to Machine B.

On Machine B (bottom), the reverse operations are done: the JSON payload is
deserialized, the events in the list unpacked and sent one by one. A
`TimeDecimate` processor keeps only one event per second, and sends them to
a `Print` processor that displays them in the console.

![Processor chain](PackerExample.png?raw=true)

This whole process takes 30 lines of code.
See the [Java code](https://liflab.github.io/beepbeep-3-examples/classnetwork_1_1httppush_1_1_packer_example.html)
that builds this processor chain.

## References and links

- [BeepBeep 3 GitHub repository](https://github.com/liflab/beepbeep-3)
- [BeepBeep 3 Palettes GitHub repository](https://github.com/liflab/beepbeep-3-palettes)
- A website with lots of detailed [code examples](https://liflab.github.io/beepbeep-3-examples)
- [Technical report](https://www.researchgate.net/publication/314092546) about Complex Event Processing in general, and BeepBeep in particular
- [Poster](https://www.researchgate.net/publication/319331563) summarizing BeepBeep in 5 minutes
- Slides from a [tutorial on BeepBeep at RV 2016](http://www.slideshare.net/sylvainhalle/when-rv-meets-cep-rv-2016-tutorial)
- [API documentation](http://liflab.github.io/beepbeep-3/javadoc/index.html)
