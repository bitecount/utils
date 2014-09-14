#include <stdio.h>
#include <stdlib.h>

typedef struct frequency
{
	int item;
	int count;
} frequency_t;

void printsubset(int* x, int i)
{
	printf("[");
	for(int j = 0; j < i; ++j)
		printf("%4d", x[j]);
	printf("]\n");
}

/*
a	: pointer to an array of frequency_t elements.
N	: size of the above array.
sum	: sum we are looking for.
result	: array where selected numbers will be stored.
index	: caller must initially setup result and index.
*/
void subsetsum(frequency_t* a, int N, int sum, int* result, int index)
{
	if(N == 0) return;

	int psum = sum - a[0].item;

	//we cannot use an element if its frequency count is <= zero.
	if(a[0].count <= 0) goto try_with_next_element;

	result[index] = a[0].item;
	//if psum is zero, we found a combination which adds up to sum, so print it. otherwise decrease the frequency
	//count of the current element and make a recursive call.
	if(psum == 0)
		printsubset(result, index + 1);
	else
	{
		--a[0].count;
		subsetsum(a, N, psum, result, index + 1);
		++a[0].count;
	}
	
try_with_next_element:
	subsetsum(a + 1, N - 1, sum, result, index);
}

int main()
{
	frequency_t a[] = { {6, 4}, {9, 3}, {3, 1} };
	int N = sizeof(a)/sizeof(*a);
	int sum = 27;
	int* result = (int*) malloc(sizeof(int) * sum);

	subsetsum(a, N, sum, result, 0);

	return 0;
}
