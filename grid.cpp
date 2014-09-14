#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct
{
	int i, j;
} pair_t;

void displaysequence(pair_t* p, int N)
{
	for(int i = 0; i < N; ++i)
		printf("(%d,%d) ", p[i].i, p[i].j);
	printf("\n");
}

/*
In the 2D array of characters 'matrix' of size M*N, find the pattern in 'pattern' starting from [i][j]. 'visited' is
a workspace which must at least be of size M*N, 'p' points to an array where the trail can be stored (length at least M*N)
and 'k' should be set to 0 by the outer caller.
Note that multiple matches are possible, 'matchcount' keeps tracks of the number of matches.
*/
int patternmatch2d(const char** matrix, int M, int N, int i, int j, char* pattern, bool* visited, pair_t* p, int k)
{
	static const pair_t neighbours[] = { {0,1}, {1,0}, {0,-1}, {-1,0} };
	int matchcount = 0;

	//Basic parameter validation.
	if(matrix == NULL || M <= 0 || N <= 0 || i < 0 || i >= M || j < 0 || j >= N || pattern == NULL
           || visited == NULL || p == NULL || k < 0)
	return 0;

	//Already visited cell, hence skip this.
	if(visited[j + i * N]) return 0;
	
	//First character in the pattern must match.
	if(matrix[i][j] == *pattern)
	{
		//Put (i,j) in the path.
		p[k].i = i; p[k].j = j;

		//If the next character in the pattern is NULL, then we have found a match, just display the path.
		if(pattern[1] == '\0')
		{
			displaysequence(p, k + 1);
			return 1;
		}

		visited[j + i * N] = true;

		//Recursive calls for all the neighbouring cells.
		for(int z = 0; z < sizeof(neighbours)/sizeof(*neighbours); ++z)
		{
			int m = i + neighbours[z].i;
			int n = j + neighbours[z].j;

			if(m >= 0 && n >= 0 && m < M && n < N)
				matchcount += patternmatch2d(matrix, M, N, m, n, pattern + 1, visited, p, k + 1);
		}
	
		visited[j + i * N] = false;
	}
	return matchcount;
}

void patternmatch2d_grid(const char** matrix, int M, int N, char* pattern)
{
	pair_t* p = (pair_t*) malloc(sizeof(pair_t) * M * N);
	bool* visited = (bool*) malloc(sizeof(bool) * M * N);
	 
	memset(visited, 0, sizeof(bool) * M * N);
	patternmatch2d(matrix, M, N, 0, 0, pattern, visited, p, 0);
	
	free(visited);
	free(p);
}

int main()
{
	const char* matrix[] = { "MICRO",
		   	         "XCOOP",
			         "AROMK",
			         "OCSOF",
			         "MISET" };

	char* pattern = "MICRO";
	patternmatch2d_grid((const char**)matrix, 5, 5, pattern);
	return 0;
}
