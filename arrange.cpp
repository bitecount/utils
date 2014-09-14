#include <stdio.h>
#include <stdlib.h>

typedef struct frequency
{
	int item;
	int count;
} frequency_t;

void printarrangement(int *x, int i)
{
	printf("[");
	for(int j = 0; j < i; ++j)
		printf("%3d ", x[j]);
	printf("]\n");
}

/*
Backtracking function to either print permutations or combinations (with repetition) of numbers.
f:	Pointer to the array of frequency_t. A frequency_t consists of an item and its frequency.
fsize:	Size of the array f points to.
x:	Pointer to an array which is used to store the generated arrangement.
i:	Index into the array x where the next element will be written.
N:	How many elements to choose. i.e. nPr or nCr N=r and fsize=n.
permute:If true permutations are generated, else combinations are generated.
*/
void arrange(frequency_t *f, int fsize, int *x, int i, int N, bool permute)
{
	//Basic parameter validation.
	if(f == NULL || fsize <= 0 || x == NULL || i < 0 || N <= 0) return;

	//We have an arrangement to be printed.
	if(i == N)
	{
		printarrangement(x, i);
		return;
	}

	//Backtracking.
	for(int j = 0; j < fsize; ++j)
	{
		if(f[j].count <= 0) continue;
		
		x[i] = f[j].item;
		--f[j].count;

		permute ?
		arrange(f, fsize, x, i + 1, N, permute) :
		arrange(f + j, fsize - j, x, i + 1, N, permute);
		
		++f[j].count;
	}
}

int main()
{
	frequency_t a[] = { {1, 1}, {2, 1}, {3, 1}, {4, 1} };
	int size = sizeof(a)/sizeof(*a);
	int* x = (int*) malloc(sizeof(int)*size);
	arrange(a, 4, x, 0, 2, false);
	return 0;
}
