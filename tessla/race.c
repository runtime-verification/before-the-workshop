#include <stdio.h>
#include <pthread.h>
#define LOOPS 100

int x = 0; // shared variable

void* count1(void *arg) {
    for ( int i = 0; i < LOOPS; i++ ) {
        x++; 
    }
    return NULL;
}

void* count2(void *arg) {
    for ( int i = 0; i < LOOPS; i++ ) {
        x++; 
    }
    return NULL;
}

int main() {
    pthread_t p1, p2;
    pthread_create( &p1, NULL, count1, NULL );
    pthread_create( &p2, NULL, count2, NULL );
    pthread_join(p1, NULL);
    pthread_join(p2, NULL);
    printf( "Counted %d\n", x );
    return 0;
}
