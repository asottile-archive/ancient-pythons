def gcd(x, y):
	while y != 0:
		tmp = x%y
		x = y
		y = tmp
	return x

def main():
	gcd(2*3*5*7*11*13, 12345678910)

main()
