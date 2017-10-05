## QEA and the MarQ tool 

- QEA = Quantified Event Automata
- MarQ = Monitoring at runtime with QEA

## Author: Giles Reger

## The Auction Site Study

Below I introduce a set of properties taken from a single setting, that of an online auction site. This example is completely artificial but is an attempt to capture something realistic. The reason for such an artificial example was to create a setting where a range of behaviours could be explored. I am keen to hear suggestions for changes to improve the realism.

### The Setting

The setting is of an online auction site where users can list items for sale and bid on items listed by other users. The entities of interest are `item`s and `user`s. One could add further entities (such as transactions, bidding sessions, online stores etc) to make the setting richer but I have chosen to keep things relatively simplistic.

We assume that the system is instrumented to log the following events where mentioned entities are identified by a unique identifier i.e. we assume that we can trivially identify items and users. Each event has as a first parameter a timestamp t given as an integer value (we ignore the units):
- `list(t,user,item,min,period)` when `user` lists `item` for sale with a `min` price over a `period` of time 
- `bid(t,user,item,amount)` when `user` bids `amount` on `item`
- `sold(t,item,user)` when `item` is sold to `user` i.e. `user` wins `item`
- `withdraw(t,item)` when `item` is withdrawn from the auction

In some examples I will also assume a `clock(time)` event that is triggered at a certin frequency. This is a hack required for my specification language that does not natively reason about time (timestamps are just integer data) and allows us to put guarantees on detecting time-bounded properties.

### Example Traces

Below is a list of short example traces which demonstrate the above events and will be used to explain some properties given later.

- **T1.** `list(1,A,hat,5,20) bid(2,B,hat,4) list(3,B,box,1,1) bid(4,C,hat,6) sold(25,hat,C)` 
- **T2.** `list(1,A,hat,5,20) bid(2,B,hat,4) bid(4,C,hat,3) sold(25,hat,D)`
- **T3.** `withdraw(1,hat) sold(1,hat)`
- **T4.** `list(1,A,hat,5,20) bid(22,B,hat,10) sold(50,hat,B)`
- **T5.** `list(1,A,hat,5,20) list(2,A,box,1,20) bid(3,B,hat,5) bid(4,B,box,4)`

### Some Properties

Below is a list of properties we want to hold over traces of such events. Given the rich setting, it should be easy to extend this list with other sensible examples. Note that an implicit property is that timestamps should be strictly increasing. I don't write this out explicitly but assume that it is always satisfied.

- **P1.** Items must be listed before being bid on and may only be listed once 
- **P2.** Bids on an item must be strictly increasing
- **P3.** An item can only be sold if the last bid was greater or equal to the minimum price. The user who wins the item is the user who made this last bid.
- **P4.** Items cannot be bid on once the listed period is over 
- **P5.** An item can only be withdrawn after it is listed and before it is sold. Once it is withdrawn it cannot be bid on or sold. 
- **P6.** A user cannot bid on their own item 
- **P7.** If a bid is made for greater than the minimum then the item must be sold within `T` time units of the end of the period (unless it is withdrawn). I leave `T` as abstract as the actual value does not matter for specification.

The above properties are all safety properties (apart from **P7**) stated positively. We can also introduce some other properties that capture likely bad behaviour that we want to detect i.e. these are stated 'negatively' so that satisfying these properties represents a potential problem.

- **P8.** There are two users `u1` and `u2` such that `u1` bids on all items listed by `u2`
- **P9.** There are two users `u1` and `u2` such that all of the items `u2` bids are listed by `u2`

These properties are meant to suggest cases where we may be suspicious that `u1` and `u2` are the same person trying to increase their own bids. Ideally we would not require this be *all* items (e.g. some high percentage instead) but this would make things harder to specify. I return to this point later on the limitations of QEA.

- **P10.** A user frequently (over 50% of the time) bids within 2 seconds of another user 

This propery is meant to detect a user using an automated tool for bidding (which we assume is agains the rules of the site).

Here is a brief summary of why some of the example traces satisfy or violated some of these properties (this list is not exhausitive).
- **T1** satisfies all properties
- **T2** violates **P2** and **P3** as bids are not increasing and no bid was made for above the minimum yet the item was sold 
- **T3** clearly violates **P5**. It also violates **P3** as this property implicitly requires a bid before an item is sold
- **T4** violates **P4** as the item is bid on after the period. It also violates **P7** for `T`<29.
- **T5** violates **P8** and **P9** as user `B` bids on exactly those items listed by user `A`

I am happy to add more examples if any properties are unclear.

### Formalised in QEA

I now formalise *some* of the above properties in QEA. I can add more formalisations but some are straightforward and I want to use the space on the less straightforward ones.

#### Formalising **P1**, **P2**, and **P3**

In the following I build up a QEA that captures properties 1-3 as these are somewhat related. In fact, all QEAs here implicitly capture **P1** as this is a basic property required to check most things.

We can specify **P1** as follows using a notation that has not been presented anywhere but has been used in a number of publications as a textual representation of the state machine definition.

```
qea(P1){
  forall(item)

  accept next state(1){
    list(_,_,item,_,_) -> 2
  }
  accept next state(2){
    bid(_,_,item,_) -> 2
  }
}
```

Let me explain a few parts:
- `forall(item)` is a quantifier saying that the state machine applies for all `item` objects
- `accept` indicates that the state is accepting/final
- `next` is a modifier that means that there is an implicit failure transition for all events that cannot make a transition i.e. the standard state machine semantics. As there is no fixed default I always either specify this or the alternative (`skip`)
- In `list(_,_,item,_,_)` I use `_` to indicate a parameter that I do not care about 
- The first state mentioned is implicitly taken to be the unique starting state

The rest should hopefully be quite self-explanatory i.e. it is a state machine. We are in state 1 if the `item` has not been listed and in state 2 after it has been listed and `bid` events are allowed.

To extend this to **P2** I add a *free variable* (perhaps not the best name) that captures some *local state* of the state machine. This `current` variable captures the current bid for the item. There is then a language of guards and assignments that can be used to check and update this state. This leads to the following straightforward extension of the previous QEA. Note that if the guard does not hold then this means that there is no matching transition and the `next` modifier means that there is an implicit failure.

```
qea(P1and2){
  forall(item)

  accept next state(1){
    list(_,_,item,_,_) do [current:=0] -> 2
  }
  accept next state(2){
    bid(_,_,item,amount) if [amount > current ] do [current:=amount]  -> 2
  }
}
```

Finally, to include **P3** we need to remember `min` from the `list` event and add a `sold` transition in state 2 that uses two new free variables `last_user` and `user` to check that the item is always sold to the last bidder. 

```
qea(P1and2and3){
  forall(item)

  accept next state(1){
    list(_,_,item,min,_) do [current:=0] -> 2
  }
  accept next state(2){
    bid(_,last_user,item,amount) if [amount > current ] do [current:=amount]  -> 2
    sold(_,item,user) if [user=last_user and current>=min] -> success
  }
}
```

The `success` state is a shorthand for an accepting state with self-looping transitions for all events. There is a symmetric `failure` state that is used later.

#### Formalising **P4**

This is another simple QEA (that also extends **P1**). Here we use the timestamp `t` and `period` information in the `list` event to record the expected `end` time. The `bid` transition is then guarded by this end time. 

```
qea(P4){
  forall(item)

  accept next state(1){
    list(t,_,item,_,period) do [end:=t+period] -> 2
  }
  accept next state(2){
    bid(t,_,item,_) if [t < end] -> 2 
  }
}
```

I note that it would be easy to add this to the `P1and2and3` QEA but we can see that things can become unreadable quite quickly.

Notice that the notion of time is not built-in to QEA but is just acheived by treating time as data.

#### Formalising **P7**

This is another property that deals with time. In the following QEA we split the previous state 2 into two states where we are in state 3 if the minimum price has been reached.

```
qea(P7){
  forall(item)

  accept next state(1){
    list(t,_,item,min,period) do [end:=t+period] -> 2 
  }
  accept next state(2){
    bid(_,_,item,amount) if [amount < min] -> 2 
    bid(t,_,item,amount) if [amount >= min] -> 3 
  }
  accept next state(3){
    sold(t,item,_) if [t < end+T] -> success 
    withdraw(t,item) if [t < end+T] -> success
    clock(t) if [t >= end+T] -> failure
  }
}
```

Here the `clock` event is used to detect failure of the time bound. If clock events occur with frequency F then we know we will detect failure within F units of time from the expiry of `end+T`.

#### Formalising **P8**

So far the quantification has just been over items. This was because I wanted to explore some of the other parts of the language. This QEA uses three quantifed variables to capture a reasonable complex property. We start by saying there exist two users forall items and then use a state machine that captures the expression

```
if u2 lists item then u1 should bid on it
```

i.e. if `u2` does not list `item` then the state machine should be accepting. This is acheived by an accepting initial state. At this point it is worth considering the semantics of quantification (which I have skipped so far). Quantifiers act to define sets of trace projections and the kind of quantifier dictates whether all or some members of that set need to be accepted. This is still quite vague and I prefer to refer the reader to publiciations/slides where I have explained these things multiple times.

```
qea(P8){
  exists(u1,u2) forall(item)

  accept skip state(1){
    list(_,u2,item,_,_) -> 2 
  }
  skip state(2){
    bid(_,u1,item,_) -> success 
  }
}
```

There is a slight problem with this QEA. If `u2` does not list any items then it is going to satisfy the property paired with any other user. We could assume that this does not happen (or check it seperately) but can also extend the QEA as follows. 

```
qea(P8b){
  exists(u1,u2) forall(item)

  skip state(1a){
    list(_,u2,item,_,_) -> 2 
    list(_,u2,other,_,_) if [other!=item] -> 1b 
  }
  accept skip state(1b){
    list(_,u2,item,_,_) -> 2 
  }
  skip state(2){
    bid(_,u1,item,_) -> success 
  }
}
```

This looks a bit odd and begins to expose some of the intracacies of the QEA language. Namely, the dependence on the alphabet. This QEA is far less efficient to monitor as we can no longer index on the `item` position as it is used with a free variable.

### Reflections (What is good at/missing etc)

This section is still quite brief and may be expanded. I focus on the missing things and what QEA is not so good at but do not mean to imply that there is nothing it is good at! Here are some points:

- QEA are not composable. If the quantifiers and alphabets are identical then we might be able to perform intersection. 
- State machines are low-level. This can make things difficult to read but also makes it difficult to introduce scoping and aggregate operators that work at a higher level of abstraction. 
- State machines are inherently regular; we can use local state/guards/assignments to implement Turing machines but this quickly becomes unreadable. I argue that the useful expressiveness of QEA has a regular quality (I acknowledge this is a wooly statement) 
- `forall` and `exists` quantifiers are quite coarse-grained, they cannot be used to express (e.g.) *for at least 90%*
- I don't have a formal definition of guard/assignment language, which prohibits full analysability
- Time is not built-in, which often requires annoying computations

## References & links

This is not a description of how to use MarQ as the focus is on the specification language but the MarQ tool is available [here](https://github.com/selig/qea).

Related publications can be found [here](http://www.cs.man.ac.uk/~regerg/publications.html). The key publiciations (by title only) are:
- Quantified Event Automata - Towards Expressive and Efficient Runtime Monitors 
- Specification of Parametric Monitors - Quantified Event Automata versus Rule Systems
- MarQ: monitoring at runtime with QEA
