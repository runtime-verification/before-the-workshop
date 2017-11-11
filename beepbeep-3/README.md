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

### Example 1: Cumulative average

![Processor chain](Average.png?raw=true)

## References and links

- [BeepBeep 3 GitHub repository](https://github.com/liflab/beepbeep-3)
- [BeepBeep 3 Palettes GitHub repository](https://github.com/liflab/beepbeep-3-palettes)
- A website with lots of detailed [code examples](https://liflab.github.io/beepbeep-3-examples)
- [Technical report](https://www.researchgate.net/publication/314092546) about Complex Event Processing in general, and BeepBeep in particular
- [Poster](https://www.researchgate.net/publication/319331563) summarizing BeepBeep in 5 minutes
- Slides from a [tutorial on BeepBeep at RV 2016](http://www.slideshare.net/sylvainhalle/when-rv-meets-cep-rv-2016-tutorial)
- [API documentation](http://liflab.github.io/beepbeep-3/javadoc/index.html)
