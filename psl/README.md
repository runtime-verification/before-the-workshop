# PSL 

## Author: Cindy Eisner
## Description


Example specifications: 

1.  If a request is acknowledged (assertion of signal *req*, followed by 3 to five cycles in which signal *busy* is asserted, followed by an assertion of *ack*), then signal *busy* should remain asserted until *done* holds.   

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Strong version -- the trace must continue until *done* is seen:

         G {req ; busy[*3:5] ; ack} |-> {busy[*] ; done}!

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Weak version -- *busy* can hold forever, or until the end of the trace:

         G {req ; busy[*3:5] ; ack} |-> {busy[*] ; done}


2.  The first occurence of *ack* after every *req* is followed by *gnt*.

         G ({req ; ack[->]} |=> gnt)

3.  Signal *dt\_complete* should be asserted if and only if a data transfer (assertion of signal *data\_start* followed by some number of assertions of *data* followed by *data\_end*) has just completed.  

         G (dt_complete <-> ended({data_start ; data[*] ; data_end}))

4.  If *p* at a positive edge of clock *clka*, then *q* at the next positive edge of *clka*

         G (p -> X q)@(posedge clka)

5.  Consecutive writes (signal *write* is asserted) cannot both be high priority writes (signal *high* is asserted together with *write*). 

         G (high -> X !high)@write


6.  Signal *q* must be asserted three cycles after *p* is asserted, unless a reset (assertion of *rst*)  has cancelled the obligation.  

         G(p -> X X X q) abort rst


7.  Whenever a read request (assertion of signal *read*) occurs, the next four data transfers (assertion of signal *data*) must have a matching tag.

         forall i in {0:7}: G((read && tag[2:0]==i) -> next_event_a(data)[1:4](tar[2:0] ==i))


## Standards

* [PSL (IEEE Std 1850<sup>Tm</sup>-2005)]{https://standards.ieee.org/findstds/standard/1850-2005.html}
* [PSL as part of VHDL (IEEE Std 1076<sup>Tm</sup>-2008)]{https://standards.ieee.org/findstds/standard/1076-2008.html}

## References & links

* [Temporal Logic Made Practical]{http://www.cis.upenn.edu/~fisman/documents/EF_HBMC14.pdf}
In  Clarke, E.M., Henzinger, Th.A., Veith, H., Bloem, R. (Eds.), Handbook of Model Checking.  Springer (to appear).  
* [A Practical Introduction to PSL]{http://www.springer.com/gp/book/9780387361239}
* [RuleBase]{https://www.research.ibm.com/haifa/projects/verification/Formal_Methods-Home/}


