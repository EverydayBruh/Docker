#include <stdio.h>
#include <time.h>

void benchmark() {
    for (long long i = 0; i < 20000000000; i++) { i=i; }
}

int main() {
    clock_t start, end;
    double cpu_time_used;

    start = clock();
    benchmark();
    end = clock();

    cpu_time_used = ((double) (end - start)) / CLOCKS_PER_SEC;

    printf("Execution time: %f seconds.\n", cpu_time_used);

    return 0;
}