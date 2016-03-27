/*

Entry point for the Windows NT DLL.

About the only reason for having this, is so initall() can automatically
be called, removing that burden (and possible source of frustration if 
forgotten) from the programmer.

This now also calls WSACleanup to clean up sockets.  The init of sockets
is done by the socketmodule, but modules have no terminate handler.
The sockets doco says it is OK to call this if not initialised, so here is
a safe place to do it.

*/
#include "windows.h"

/* NT and Python share these */
#undef INCREF
#undef DECREF

#include "allobjects.h"
BOOL	WINAPI	DllMain (HANDLE hInst, 
						ULONG ul_reason_for_call,
						LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
		case DLL_PROCESS_ATTACH:
			initall();
			break;
		case DLL_PROCESS_DETACH:
			break;

	}

	return TRUE;
}
