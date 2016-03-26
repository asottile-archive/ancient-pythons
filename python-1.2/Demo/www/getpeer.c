#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/un.h>
#include <netdb.h>

main() {
	struct sockaddr_in addr;
	int addrlen;
	long x;

	addrlen = sizeof addr;
	if (getpeername(0, (struct sockaddr *) &addr, &addrlen) < 0) {
		perror("getpeername(0)");
		exit(1);
	}
	x = ntohl(addr.sin_addr.s_addr);
	printf("%d.%d.%d.%d\n",
		(int) (x>>24) & 0xff, (int) (x>>16) & 0xff,
		(int) (x>> 8) & 0xff, (int) (x>> 0) & 0xff);
	exit(0);
}
