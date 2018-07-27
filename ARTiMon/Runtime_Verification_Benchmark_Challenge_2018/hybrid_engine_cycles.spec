* // trace signals
cycleid
distance
elecpower
socelec
fuelpower
socfuel
speed
* // intermediate formulas
false = 'bool_cst' 0
zero = 'double_cst' 0
ms = 'double_cst' 131.31
br = 'double_cst' -1.7
cbat = 'double_cst' 1602180
aFC = 'double_cst' 2.5

cycle_end = Bot cycleid
cycle_stable = ! cycle_end
ep_zero_vec[2] elecpower zero
ep_neg = # (('<' ep_zero_vec) & elecpower)
ep_neg_integ =  # ( '*' ( LI ep_neg))
ep_neg_integ_reset =  #r (cycle_stable & ep_neg_integ)
integral = A{'sum'}[<,0] ep_neg_integ_reset
integral_trans = cycle_end & integral
div_cbat_vec[2] integral_trans cbat
prop_vec[2] ('div' div_cbat_vec) br
prop_c = cycle_end -> ('<' prop_vec)

// prop a
speed_by_cycle = #r (cycle_stable & speed)
greatest_speed = (A{'greatest'}[<,0] speed_by_cycle)
greatest_end_cycle = cycle_end & greatest_speed
prop_a_vec[2] greatest_end_cycle ms
greatest_exceed_ms = '>' prop_a_vec
prop_a = cycle_end -> greatest_exceed_ms

// prop b

socfuel_resize_vec[2] socfuel ('double_cst' 4500)
socf_sized = '*' socfuel_resize_vec

socfuel_at_start = (Top0 cycleid) & socf_sized
socfuel_at_end =  cycle_end & (A{':='} [<,0] socf_sized)
socfuel_delta_vec[2] (A{':='} [<,0] socfuel_at_start) socfuel_at_end 
delta_socf = '-' socfuel_delta_vec

distance_at_start = (Top0 cycleid) & distance
distance_at_end =  cycle_end & (A{':='} [<,0] distance)
distance_delta_vec[2]   distance_at_end (A{':='} [<,0] distance_at_start)
delta_d = '-' distance_delta_vec

dsoc_dd_vec[2] delta_socf delta_d
dsoc_dd = 'div' dsoc_dd_vec

prop_b_vec[2] dsoc_dd aFC
prop_b = cycle_end -> ('<' prop_b_vec)

* 
hazar_c = ! prop_c
hazard_a = ! prop_a
hazard_b = ! prop_b