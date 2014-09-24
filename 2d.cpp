#include <utils.h>

#define INDEX(i, j, m, n) (i * n + j)
#define BLOCKED_POSITION (-1)

const pair_t neighbours[] = { {0,1}, {1,0}, {0,-1}, {-1,0} };
const int neighbours_size = sizeof(neighbours)/sizeof(*neighbours);

void REVERSE_INDEX(int k, int m, int n, int& i, int& j)
{
	i = k / n;
	j = k % n;
}

void print_trail(int* trail, int index, int m, int n)
{
	int u, v;
	for(int i = 0; i < index; ++i)
	{
		if(trail[i] & 0x8000)
		{
			REVERSE_INDEX(trail[i] & (~ 0x8000), m, n, u, v);
			printf("Move A to (%d,%d)\n", u + 1, v + 1);
		}
		else
		{
			REVERSE_INDEX(trail[i], m, n, u, v);
			printf("Move B to (%d,%d)\n", u + 1, v + 1);
		}
	}
}

void display_grid(int** grid, int m, int n, pair_t a, pair_t b)
{
	for(int i = 0; i < m; ++i)
	{
		for(int j = 0; j < n; ++j)
		{
			if(a.i == i && a.j == j) printf(" A ");
			else if(b.i == i && b.j == j) printf(" B ");
			else if(grid[i][j] == 0) printf(" 0 ");
			else printf(" * ");
		}
		printf("\n");
	}
}

typedef struct position_state
{
	int** grid;
	int m, n;
	int c1, c2, f1, f2;
	int** visited1, **visited2;
	int* trail, index;
	int* done;
} position_state_t;

enum
{
	CAN_VISIT = 0,		//initial state - we can visit this cell.
	VISITED_ONCE = 1,	//the cell has been visited once.
	CAN_VISIT_AGAIN = 2,	//the cell is marked to allow one more visit.
	VISITED = 3		//the cell is visited twice, and further visits are not possible.
};

inline bool can_visit(const int v)
{
	return (v == CAN_VISIT || v == CAN_VISIT_AGAIN) ? true : false;
}

inline void mark_visited(int& v)
{
	switch(v)
	{
		case CAN_VISIT:
		case CAN_VISIT_AGAIN: ++v;
	}
}

inline void clear_visited(int& v)
{
	switch(v)
	{
		case VISITED_ONCE:
		case VISITED: --v;
	}
}

inline void mark_can_visit_again(int& v)
{
	switch(v)
	{
		case VISITED_ONCE: ++v;
	}
}

void exchange_position(position_state_t state)
{
	if(state.c1 == state.f1 && state.c2 == state.f2)
	{
		print_trail(state.trail, state.index, state.m, state.n);
		*(state.done) = 1;
		return;
	}	

	if(*(state.done) == 1) return;

	//try to advance 'A'.
	for(int i = 0; i < neighbours_size; ++i)
	{
		int u, v;
		REVERSE_INDEX(state.c1, state.m, state.n, u, v);
		u += neighbours[i].i; v += neighbours[i].j;

		if(u >= 0 && u < state.m && v >= 0 && v < state.n)
		{
			//neighbour location (u,v) which is within the grid.
			int t = INDEX(u, v, state.m, state.n);
			//the grid position should not be blocked, already visited by 'A' or presently occupied by 'B'.
			if(state.grid[u][v] == BLOCKED_POSITION || !can_visit(state.visited1[u][v]) || t == state.c2) continue;
		
			mark_visited(state.visited1[u][v]);
			int temp = state.visited2[u][v];
			mark_can_visit_again(state.visited2[u][v]);
			state.trail[state.index] = t | 0x8000;
			
			position_state_t newstate = state;
			newstate.c1 = t;
			newstate.index++;
			exchange_position(newstate);

			//restore the state of visited matrix.
			state.visited2[u][v] = temp;
			clear_visited(state.visited1[u][v]);
		}
	}

	//try to advance 'B'.
	for(int i = 0; i < neighbours_size; ++i)
	{
		int u, v;
		REVERSE_INDEX(state.c2, state.m, state.n, u, v);
		u += neighbours[i].i; v += neighbours[i].j;

		if(u >= 0 && u < state.m && v >= 0 && v < state.n)
		{
			//neighbour location (u,v) which is within the grid.
			int t = INDEX(u, v, state.m, state.n);
			//the grid position should not be blocked, already visited by 'B' or presently occupied by 'A'.
			if(state.grid[u][v] == BLOCKED_POSITION || !can_visit(state.visited2[u][v]) || t == state.c1) continue;

			mark_visited(state.visited2[u][v]);
			int temp = state.visited1[u][v];
			mark_can_visit_again(state.visited1[u][v]);
			state.trail[state.index] = t;

			position_state_t newstate = state;
			newstate.c2 = t;
			newstate.index++;
			exchange_position(newstate);

			//restore the state of visited matrix.
			state.visited1[u][v] = temp;
			clear_visited(state.visited2[u][v]);
		}
	}
}

int main()
{
	int m, n;
	m = 2, n = 5;

	int** grid = allocate_2d_array(m, n);

	int ** v1 = allocate_2d_array(m, n);
	int ** v2 = allocate_2d_array(m, n);

	int * trail = (int*) calloc(m*n*10, sizeof(int));
	int index = 0;
	int done = 0;

	grid[1][1] = -1;
	grid[1][3] = -1;

	pair_t a, b;

	a.i = 1; a.j = 0;
	b.i = 1; b.j = 2;

	int p1 = INDEX(a.i, a.j, m, n);
	int p2 = INDEX(b.i, b.j, m, n);

	v1[a.i][a.j] = v2[b.i][b.j] = VISITED_ONCE;

	display_grid(grid, m, n, a, b);

	position_state_t state;
	state.grid = grid;
	state.m = m; state.n = n;
	state.c1 = p1; state.c2 = p2;
	state.f1 = p2; state.f2 = p1;
	state.visited1 = v1;
	state.visited2 = v2;
	state.trail = trail;
	state.index = index;
	state.done = &done;

	exchange_position(state);	

	return 0;
}
