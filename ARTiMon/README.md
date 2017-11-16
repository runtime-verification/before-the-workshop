# RV Challenge & Cheat Sheet (max 2 pages)

## ARTiMon Specification Language
## Author(s): Nicolas RAPIN
## Description: Hybrid Engine Trace Analysis

Consider including the following and introducing additional structure if you want.

* My favourite specification (or two)
	
	ARTiMon input langage (a mix of MITL & STL with additionnal operators like the Aggregation, Cumulative Length, Last, Generalized Rising/falling edges, Duration ...)
	
	See the paper "ARTiMon Monitoring Tool, The Time Domains" of post-proceedings of RV-CuBES 2017 for more details about the language.
	
	(Some difference with the effective syntax of the tool may exists)

* A short paragraph explaining the property

	The system under monitoring is a vehicule hybrid engine.
	
	The goal is to check/compute three properties about those quantities:
	
		(a) the average consumption 
		
		(b) the max speed
		
		(c) the rate of electric power recover
		
	Those quantities shall be considered not on the overall trace but per cycle. The cycle variable is identified by an integer.
	So the monitor must be able to spot cycles starts and ends and to restrict a quantity computation to a cycle.
	
	The Files for executing ARTiMon are in the directory SherpaEngineCycles.
	
	The executable has been compiled with Cygwin compiler under Windows 7 for 64 bits. Cygwin' dll may be required to execute properly.
	
	The environment variable ARTIMON must be defined (though not used ... so an arbitrary value or path is fine). 
	
	The specification file for criterion (c) is cycles.spec. 
	
	The file cycles_all_criteria.spec contains all criteria (a), (b), (c)
	
	Here ARTiMon is used to compute some function rather than for computing a boolean verdict of a boolean hazard.
	
	In order to do that monitored hazards have the form: f & false where f is the non-boolean function specifying the criterion

	For criterion (c) the final term representing this criterion is 'div' (integrale_pe_by_cycle_at_end, 16021800):
	
	ARTiMon vedict file (Verdict_full.html) exhibits  this line for this term: 
	'div' (integrale_pe_by_cycle_at_end, 16021800) with CI [0.1625, 7200.44[ : 
	[1800.04, 1800.04]^-0.179390314  [3600.14, 3600.14]^-0.193000664  [5400.14, 5400.14]^-0.193001817  [7200.24, 7200.24]^-0.193001841  
	
	The values attached to intervals (one for each ends of cycles) are the values computed by ARTiMon for criterion (c)
	
	Notice that they are equal to values computed with Excel by hand. 
	
* Show how to run it (if a tools exists): command line/web-based

	Just Double-Clic on ARTiMon.exe
	
* What is your formalism good at/what is missing? Application area?
* If possible, use the table from the [STTT-paper](https://link.springer.com/article/10.1007%2Fs10009-017-0454-5) to self-categorize tool

## References & links

* some URL
* an attached spec & input for download if applicable

## Nice-to-haves

* do you have an "online playground" to run your example?

	No (Not Allowed By Our Instititute)
