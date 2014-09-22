#ifndef __UTILS_H__
#define __UTILS_H__

#include <stdlib.h>
#include <stdio.h>
#include <limits.h>

int** allocate_2d_array(int m, int n)
{
	if(m <= 0 || n <= 0) return NULL;

	char* memory = (char*) calloc((m * n * sizeof(int) + m * sizeof(int*)), sizeof(char));
	int *block, **p = NULL;

	if(memory != NULL)
	{
		p = (int**) memory;
		block = (int*) (p + m);

		for(int i = 0; i < m; ++i, block += n)
			p[i] = block;
	}
	return p;
}

void free_2d_array(void* m)
{
	free(m);
}

int* allocate_1d_array(int m)
{
	if(m <= 0) return NULL;

	return (int*) calloc(m, sizeof(int));
}

void free_1d_array(void* m)
{
	free(m);
}

typedef struct pair
{
	int i, j;
} pair_t;

int** scan_2d_array(int m, int n)
{
	int** x = allocate_2d_array(m, n);
	if(x)
	{
		printf("Elements of the (%d*%d) array:\n", m, n);
		for(int i = 0; i < m; ++i)
		for(int j = 0; j < n; ++j)
		scanf("%d", &x[i][j]);
	}
	return x;
}

int* scan_1d_array(int m)
{
	int* x = allocate_1d_array(m);
	if(x)
	{
		printf("Elements of the array of size (%d):\n", m);
		for(int i = 0; i < m; ++i)
		scanf("%d", &x[i]);
	}
	return x;
}

void print_1d_array(int* x, int m)
{
	if(x == NULL || m <= 0) return;
	for(int i = 0; i < m; ++i)
		printf("%3d", x[i]);
	printf("\n");
}

inline int max(int x, int y) { return (x > y) ? x : y; }
inline int min(int x, int y) { return (x < y) ? x : y; }
inline int swap(int* x, int* y) { int temp = *x; *x = *y; *y = temp; }

//checks if b can be obtained by rotating the matrix 'a' counter clockwise.
bool is_90_rotation(int** a, int** b, int m, int n)
{
	for(int i = 0; i < m; ++i)
	for(int j = 0; j < n; ++j)
	if(a[i][j] != b[n-1-j][i])
		return false;

	return true;
}

bool is_180_rotation(int** a, int** b, int m, int n)
{
	for(int i = 0; i < m; ++i)
	for(int j = 0; j < n; ++j)
	if(a[i][j] != b[m-1-i][n-1-j])
		return false;

	return true;
}

bool is_270_rotation(int** a, int** b, int m, int n)
{
	for(int i = 0; i < m; ++i)
	for(int j = 0; j < n; ++j)
	if(a[i][j] != b[j][m-1-i])
		return false;

	return true;
}

bool is_0_rotation(int** a, int** b, int m, int n)
{
	for(int i = 0; i < m; ++i)
	for(int j = 0; j < n; ++j)
	if(a[i][j] != b[i][j])
		return false;

	return true;
}

#endif
