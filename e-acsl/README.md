# E-ACSL (both a specification language and a tool)

## Authors

* specification language: Julien Signoles
  (derived from ACSL designed by Patrick Baudin, Pascal Cuoq,
   Jean-Christophe Filliâtre, Claude Marché, Benjamin Monate, Yannick Moy, 
   and Virgile Prevosto)
* tool (Frama-C plug-in E-ACSL): Julien Signoles and Kostyantyn Vorobyov

## Description

* checking C undefined behaviors

All the E-ACSL specifications required to detect a wide class of undefined
behaviors are automatically generated and monitored through

```
$ e-acsl-gcc.sh -c --rte=all my_favorite_files.c
```

This command generates 3 files:
./a.out:
        uninstrumented binary (as compiled by gcc)
./a.out.frama-c:
        generated C source code containing the formal E-ACSL specifications
        and the inline monitor
./a.out.e-acsl:
        instrumented binary that monitors the E-ACSL specifications encoding the
        undefined behaviors (compilation of ./a.out.frama-c by gcc)

* checking C function contract

```c
/*@ requires \forall integer i; 0 <= i < len ==> \valid(a+i);
  @ requires 0 <= idx < len;
  @ 
  @ behavior not_found:
  @   assumes \forall integer i; 0 <= i < len ==> a[i] != value;
  @   assigns \nothing;
  @   ensures \result == -1;
  @   
  @ behavior found_same_index:
  @   assumes \exists integer i; 0 <= i < len && a[i] == value;
  @   assumes a[idx] == value;
  @   assigns \nothing;
  @   ensures \result == idx;
  @   
  @ behavior found_and_replace:
  @   assumes \exists integer i; 0 <= i < len && a[i] == value;
  @   assumes a[idx] != value;
  @   assigns a[idx], a[\result];
  @   ensures a[idx] == value;
  @   ensures a[\result] == \old(a[idx]);
  @   
  @ complete behaviors;
  @ disjoint behaviors;
  @*/
int replace(int* a, int len, int idx, int value) {
  int i = 0;
  /*@ loop assigns i;
    @ loop invariant 0 <= i <= len;
    @ loop invariant \forall integer j; 0 <= j < i ==> a[j] != value;
    @ loop variant len - i; */
  for(; i < len; i++)
    if (a[i] == value) break;
  if (i == len) return -1;
  if (a[idx] == value) return idx;
  a[i] = a[idx];
  a[idx] = value;
  return idx; // instead of 'return i;'
}

int main(void) {
  int a[10];
  for(int i = 0; i < 10; i++) a[i] = i;
  replace(a, 10, 5, 7);
  return 0;
}
```

The function contract is enclosed in /*@ ... */ special comment.
It specifies 2 preconditions and 3 behaviors that specifies the postcondition.

Preconditions:
- 'a' must be a correctly-allocated array of 'len' cells
- 'idx' should be between 0 (large) and 'len' (strict)

Behavior 'not_found':
  if there is no 'a[i]' equal to 'value', then the function result is -1 and
  the function has no observable memory effect (meaning of 'assigns \nothing').

Behavior 'found_same_index':
  if 'a[idx]' is equal to 'value', then the function result is 'idx' and 
  the function has no observable memory effect.

Behavior 'found_and_replace':
  if there is an index 'i' different from 'idx' such that 'a[i] == value', then
  the function swaps 'a[i]' and 'a[idx] and returns 'i'.
  The only memory locations that may change are 'a[idx]' and 'a[i]'.

'complete behaviors' specifies that the 3 behaviors cover all the possible
contexts.

'disjoint behaviors' specifies that the 3 behaviors are pairwise disjoint
(no overlapping of 'assumes').

Currently, the tool E-ACSL is not able to verify neither the 'assigns' clauses
nor completeness/disjointness, but checks all the other properties.
For instance, here the last statement of replace ('return idx;') is buggy and
violates the very last postcondition 'ensures a[\result] == \old(a[idx]);':

```
$ e-acsl-gcc.sh -c replace.c
$ ./a.out.e-acsl
Postcondition failed at line 20 in function replace.
The failing predicate is:
\old((\exists integer i; 0 <= i < len && *(a + i) == value) &&
     *(a + idx) != value) ==>
*(\old(a) + \result) == \old(*(a + idx)).
Abandon
```

* checking well-ordering of C function calls

The Aorai plug-in of Frama-C provides support for specifying accepted sequences
of function calls. Accepted formats are ya automata (in Ya language) and Buchi
automata (in Promela language). Here is a small example of a Ya automate:

```
%init: init;
%accept: OK;
%deterministic;

init:
  { mode == 1 } -> mode1
| { mode == 2 } -> mode2;

mode1: { [ f(); g() ] } -> OK;
mode2: { [ g()+; h() ] } -> OK;

OK: -> OK;
```

It specifies that there are 2 modes: if 'mode == 1', then function 'f' must be 
called before function 'g', and if 'mode == 2', then function 'g' must be 
called at least once before function 'h'.

Assuming a C code, Aorai is able to add pieces of C code and ACSL annotations
to check that the initial code satisfies this specification:

```
$ frama-c my-file.c -aorai-automata spec.ya -aorai-output-c-file generated.c
```

Then E-ACSL is able to verify it:

```
$ e-acsl-gcc.sh -c -X generated.c
```

## References & links

* [E-ACSL webpage](http://www.frama-c.com/eacsl.html)
* [E-ACSL Reference Manual](http://www.frama-c.com/download/e-acsl/e-acsl.pdf)
* [What part of the language is currently supported by the tool](http://www.frama-c.com/download/e-acsl/e-acsl-implementation.pdf)
* [E-ACSL User Manual](http://www.frama-c.com/download/e-acsl/e-acsl-manual.pdf)
* [Paper about the specification language](http://julien.signoles.free.fr/publis/2013_sac.pdf)
* [E-ACSL's RV-CuBES'17 Tool Paper](http://julien.signoles.free.fr/publis/2017_rvcubes_tool.pdf)
