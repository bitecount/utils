#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

int** allocate_2d_array(int m, int n)
{
	if(m <= 0 || n <= 0) return NULL;

	char* memory = (char*) malloc( sizeof(char) * (m * n * sizeof(int) + m * sizeof(int*)) );
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

/*
a[0..N] N+1 integers
b[1..N] N operators 
*/

int calc(int a, char c, int b)
{
	switch(c)
	{
		case '+': return a + b;
		case '-': return a - b;
		case '*': return a * b;
		case '/': if(b) return a / b;
	}
	return INT_MIN;
}

int maximize_expression_r(int i, int j, int *a, char *b, int** table, int** steps)
{
	if(table[i][j] != INT_MIN) return table[i][j];

	if(i == j) return (table[i][j] = a[j]);

	int max = INT_MIN;
	for(int k = i; k < j; ++k)
	{
		int v1 = maximize_expression_r(i, k, a, b, table, steps);
		int v2 = maximize_expression_r(k+1, j, a, b, table, steps);
		int r = calc(v1, b[k+1], v2);
		if(r > max)
		{
			max = r;
			steps[i][j] = k;
		}
	}
	return (table[i][j] = max);
}

typedef enum { TYPE_OPERAND = 0, TYPE_OPERATOR = 1 } etree_node_type_t;
typedef struct etree_node
{
	etree_node_type_t type;
	union {
		int operand;
		char op;
	};
	etree_node *left, *right;
} etree_node_t;

etree_node_t* create_expression_tree(int* a, char* c, int i, int j, int** steps)
{
	etree_node_t * newnode = (etree_node_t*) malloc(sizeof(etree_node_t));
	newnode->left = newnode->right = NULL;	

	int k;

	if(i == j)
	{
		newnode->type = TYPE_OPERAND;
		newnode->operand = a[i];
	}
	else
	{
		k = steps[i][j];
		newnode->type = TYPE_OPERATOR;
		newnode->op = c[k + 1];
		newnode->left = create_expression_tree(a, c, i, k, steps);
		newnode->right = create_expression_tree(a, c, k + 1, j, steps);
	}
	return newnode;
}

void print_expression_tree(etree_node_t* root)
{
	if(root == NULL) return;

	if(root->left == NULL && root->right == NULL)
		printf("%d", root->operand);
	else
	{
		printf("(");
		print_expression_tree(root->left);
		printf("%c", root->op);
		print_expression_tree(root->right);
		printf(")");
	}
}

void print_expression(int* a, char* c, int N, int** steps)
{
	print_expression_tree( create_expression_tree(a, c, 0, N, steps) );
}

int maximize_expression(int* a, char* b, int N)
{
	int** table = allocate_2d_array(N + 1, N + 1);
	int** steps = allocate_2d_array(N + 1, N + 1);

	for(int i = 0; i <= N; ++i)
		for(int j = 0; j <= N; ++j)
			steps[i][j] = table[i][j] = INT_MIN;

	int m = maximize_expression_r(0, N, a, b, table, steps);
	print_expression(a, b, N, steps);

	free(steps);
	free(table);
	return m;
}

int main()
{
	int n = 3;
	char b[] = { ' ', '*', '+', '+'};
	int a[] = { 2, 4, 5, 2 };

	printf("Maximizing... ");
	for(int i = 1; i <= n; ++i)
		printf("%d %c ", a[i-1], b[i]);
	printf("%3d\n", a[n]);

	printf(" = %d\n", maximize_expression(a, b, n));

	return 0; 
}
