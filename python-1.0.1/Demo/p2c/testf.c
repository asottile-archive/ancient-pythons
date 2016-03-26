
int foo(int x,
	int y)
{
	printf("\n");
	printf("%d\n", x);
	printf("%d ", x);
	printf("foo ( x = %d , y = %d )\n", x, y);
	while (1) {
		if (x < y) {
			x = x+1;
			printf("%d %d\n", x, y);
			if (x == 100) {
				break;
			}
		}
		else {
			printf("uit de loop gevallen\n");
			break;
		}
	}
	printf("more\n");
}


int main()
{
	foo(90, 110);
}

