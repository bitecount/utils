#include "utils.h"

void print_swap_operation(int i, int j)
{
	printf("Swap %d and %d\n", ++i, ++j);
}

/*
sort an array consisting only of the elements {0, 1, 2} by making a minimum number of swaps. returns the number of swaps made.
*/
int sort_012(int* x, int i, int j)
{
	int count = 0;
	int l, r;

#define SWEEP_k_TO_LEFT(k) do { \
	l = i, r = j; \
	while(l < r) { \
		if(x[l] > k && x[r] == k) { \
			swap(x + l, x + r); \
			print_swap_operation(l, r); \
			++count; ++l; --r; \
		} \
		else if(x[l] <= k) ++l; \
		else --r; \
	} \
} while(0)

	SWEEP_k_TO_LEFT(0);
	SWEEP_k_TO_LEFT(1);
	
	return count;
#undef SWEEP_k_TO_LEFT
}

int main()
{
	int N = 10;

	int* x = scan_1d_array(N);
	int c = sort_012(x, 0, N - 1);
	print_1d_array(x, N);
	printf("Number of swaps required = %d\n", c);
	return 0;
}
