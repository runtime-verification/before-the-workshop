* // signaux
no_cycle
distance
puissance_elec
sOC_Elec
puissance_Fuel
sOC_Fuel
speed
* // sous_formules
false = ('bool_cst' 0)

cycle_start = Top0 no_cycle

in_cycle = ! cycle_start

cycle_end = Bot no_cycle

cycle_stable = ! (E[-0.0625,0] cycle_end)

just_before_cycle_end = V[0.0625 ] cycle_end

//---------- pour crit_a -----------

// calcul de  D(sOC_Fuel)
	
// sOC_Fuel * 4500 = Fuel en volume

	sOC_Fuel_array[2] sOC_Fuel ('double_cst' 4500)
	sOC_Fuel_volume = '*' sOC_Fuel_array

// On garde les valeurs du volume Fuel aux instants où un cycle démarre
// pour rappel l'opérateur & est interprété comme une coupure dans b & s
// lorsque b est booléen et s non booléen

	sOC_Fuel_at_cycle_start = cycle_start & sOC_Fuel_volume
	
// on prolonge cette valeur tant qu'elle ne change pas avec Ls (opérateur Last)
// on coupe avec cycle_end
// du coup sOC_Fuel_start_at_end n'est définie que quand un cycle se termine à ces instants
// vaut la valeur du volume du début de cycle précédent
// on ajoute le prolongement ] sinon la coupure est vide (en effet les signaux de base sont des fonctions sur des semi-ouverts à droite)

	sOC_Fuel_start_at_end = cycle_end & (V[-0.0625] (Ls sOC_Fuel_at_cycle_start)) 

// valeur du volume en fin de cycle
	sOC_Fuel_at_end = cycle_end & sOC_Fuel_volume

// on met les deux valeurs dans un tableau pour en faire la différence
	_D_sOC_Fuel_[2] sOC_Fuel_at_end sOC_Fuel_start_at_end

// Calcul de D(sOC_Fuel)
	_D_sOC_Fuel = '-' _D_sOC_Fuel_

// même principe pour D(distance)	
	distance_at_start = cycle_start & distance
	distance_start_at_end =  ( cycle_end) & (V[-0.0625](Ls distance_at_start))
	distance_at_end = 	cycle_end & distance
	_D_distance_[2] distance_at_end distance_start_at_end
	_D_distance = '-' _D_distance_


conso_moyenne_[2] _D_sOC_Fuel _D_distance 


//---------- pour crit_b -----------

speed_by_cycle = # ((! cycle_end) & speed)
greatest_speed_by_cycle = A{'greatest'}[<=,0] speed_by_cycle

//---------- pour crit_c -----------

// conversion en entier 0/1 de la proposition booléenne "puissance_elec < 0"
	pe_negative_array[2] puissance_elec ('double_cst' 0)
	pe_negative_int = # ('<' pe_negative_array)

// restriction de la puissance aux instants où elle négative 
	pe_negative_or_null_[2] pe_negative_int puissance_elec
	pe_negative_or_null =  '*' pe_negative_or_null_
	
//	coupure par cycle et complétion à null des instants non définis
	pe_negative_or_null_by_cycle = # (cycle_stable & pe_negative_or_null)

//	surfaces élémentaires 
	li_pe_neg = (LI pe_negative_or_null_by_cycle)
	pe_neg_surface = '*' li_pe_neg

// intégrale par cycle
	integrale_pe_by_cycle =  (A{'sum'}[<=,0] pe_neg_surface)
	
// intégrale au moment de la fin de cycle

	integrale_pe_by_cycle_at_end =  (just_before_cycle_end & integrale_pe_by_cycle)
	
integ_sur_cbat_vec[2] integrale_pe_by_cycle_at_end ('double_cst' 16021800)


*
//crit_a = ('div' conso_moyenne_)  & false 

//crit_b = (just_before_cycle_end & greatest_speed_by_cycle)  & false

crit_c =  ('div' integ_sur_cbat_vec) & false