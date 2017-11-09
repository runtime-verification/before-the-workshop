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
