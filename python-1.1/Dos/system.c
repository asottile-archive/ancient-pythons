/*---------------------------------------------------------------------------*
 * Emulation of system() under Windows.  (MS QuickWin)
 *
 * Copyright 1994, David Gottner
 *
 *                    All Rights Reserved
 *
 * Permission to use, copy, modify, and distribute this software and its
 * documentation for any purpose and without fee is hereby granted,
 * provided that the above copyright notice, this permission notice and
 * the following disclaimer notice appear unmodified in all copies.
 *
 * I DISCLAIM ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING ALL
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS.  IN NO EVENT SHALL I
 * BE LIABLE FOR ANY SPECIAL, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY
 * DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA, OR PROFITS, WHETHER
 * IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
 * OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 *
 * Nevertheless, I would like to know about bugs in this library or
 * suggestions for improvment.  Send bug reports and feedback to
 * davegottner@delphi.com.
 *---------------------------------------------------------------------------*/

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#ifdef _WINDOWS
#include <windows.h>
#include <toolhelp.h>


/*---------------------------------------------------------------------------*
 * IMPORTANT NOTE:
 *     Even though this is a QuickWin app, you must compile this module
 *     with the flags -GA -GEd in place of -Mq, so that the callback loads
 *     the data segment correctly.
 *
 * These variables are set by the callback notification function
 * and accessed by system()
 */
static BOOL taskRunning   = FALSE;
static int  taskExitValue = 0;



BOOL CALLBACK __export ChildProcNotifiee(WORD reason, DWORD info)
{
	if (reason == NFY_EXITTASK) {
		taskRunning = FALSE;
		taskExitValue = LOWORD(info);
	}

	return FALSE;
}



int system(const char *s)
{
	TASKENTRY	taskinfo;
	HINSTANCE	ourInstance;
	HTASK		ourTask;
	BOOL		task_found;
	FARPROC		notify_cb;

	ourInstance = WinExec(s, SW_SHOWNORMAL);
	if (ourInstance < HINSTANCE_ERROR)
		return ((int) ourInstance) + 1;

	/*** Get the TASK corresponding with this instance ***/
	taskinfo.dwSize = sizeof(TASKENTRY);
	task_found = TaskFirst(&taskinfo);
	while (task_found) {
		if (taskinfo.hInst == ourInstance) {
			ourTask = taskinfo.hTask;
			break;
		}

		task_found = TaskNext(&taskinfo);
	}

	/*** Install the notify callback so we can watch the child ***/
	taskRunning = TRUE;
	if (!task_found || !NotifyRegister(ourTask, ChildProcNotifiee, NF_NORMAL)) {
		MessageBox(NULL,
					"A notify callback could not be installed."
					"  This is likely a problem with the DOS module.",
					"Internal Error",
					MB_TASKMODAL | MB_ICONEXCLAMATION | MB_OK);
		TerminateApp(ourTask, NO_UAE_BOX);
		taskRunning = FALSE;
	}

	/*** Wait for completion; child will update taskRunning & taskExitValue ***/
	while (taskRunning)
		_wyield();

	return taskExitValue << 8;
}

#endif /* _WINDOWS */
