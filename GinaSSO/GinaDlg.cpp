#include "stdafx.h"
#include "GinaDlg.h"
#include <stdio.h>
#include <stdlib.h>
#include <winsock2.h>

// MSGINA dialog box IDs.
#define DEFAULT_IDD_WLXDISPLAYSASNOTICE_DIALOG		1400
// updated by Itai Shaham 02.09.07
#define DEFAULT_IDD_WLXLOGGEDOUTSAS_DIALOG			1500
// added by Rudy 3.10.07
#define DEFAULT_IDD_WLXDISPLAYLOCKEDNOTICE_DIALOG	1900
#define DEFAULT_IDD_WLXLOGGEDONSAS_DIALOG			1950
#define DEFAULT_IDD_USER_MESSAGE_DIALOG				2500


// MSGINA control IDs
// updated by Itai Shaham 02.09.07
#define DEFAULT_IDC_WLXLOGGEDOUTSAS_USERNAME   1502
#define DEFAULT_IDC_WLXLOGGEDOUTSAS_PASSWORD   1503
#define DEFAULT_IDC_WLXLOGGEDOUTSAS_DOMAIN     1504
// updated by Rudy Kirzhner  3.10.07
#define DEFAULT_IDC_WLXLOGGEDONSAS_USERNAME   1953
#define DEFAULT_IDC_WLXLOGGEDONSAS_PASSWORD   1954
#define DEFAULT_IDC_WLXLOGGEDONSAS_DOMAIN     1956

#define DEFAULT_RestartCredentialsListener	1
#define DEFAULT_PresentLogonMessage			1

//updated by Rudy Kirzhner 06.09.07
// added support for recieving credentials via a pipe
#define PIPE_BUFSIZE 1024

// Pointers to redirected functions.
static PWLX_DIALOG_BOX_PARAM pfWlxDialogBoxParam = NULL;

// Pointers to redirected dialog box.
static DLGPROC pfWlxLoggedOutSASDlgProc		= NULL;
static DLGPROC pfWlxLoggedOnSASDlgProc		= NULL;
static DLGPROC pfWlxDisplaySASNoticeDlgProc	= NULL;
static DLGPROC pfWlxDisplayLockedNoticeDlgProc	= NULL;
static DLGPROC pfWlxUserMessageDlgProc	= NULL;

static LPTSTR lpszPipename = L"\\\\.\\pipe\\VDSMDPipe"; 
static PVOID g_pWinlogonFunctions = NULL;
static HANDLE g_hWlx = NULL;
extern DWORD g_dwVersion = WLX_VERSION_1_4;
static HANDLE hPipe =NULL;
static	DWORD dwThreadId=0;
static	HANDLE hThread=NULL;
static BOOL l_bAttemptedToLogin = FALSE;

struct GlobalConfig
{
	int m_IDD_WLXDISPLAYSASNOTICE_DIALOG;//		1400 - ms
	int m_IDD_WLXLOGGEDOUTSAS_DIALOG;//			1500 - ms
	int m_IDD_WLXLOGGEDONSAS_DIALOG;//			1950 - ms
	int m_IDD_WLXDISPLAYLOCKEDNOTICE_DIALOG;//		1900- ms
	int m_IDC_WLXLOGGEDOUTSAS_USERNAME;//   1502- ms
	int m_IDC_WLXLOGGEDOUTSAS_PASSWORD;//   1503- ms
	int m_IDC_WLXLOGGEDOUTSAS_DOMAIN ;//    1504- ms
	int m_IDC_WLXLOGGEDONSAS_USERNAME;//   1953- ms
	int m_IDC_WLXLOGGEDONSAS_PASSWORD;//   1954- ms
	int m_IDC_WLXLOGGEDONSAS_DOMAIN;//     1956- ms
	int m_IDD_USER_MESSAGE_DIALOG;//     2500- ms
	BOOL m_bRestartCredentialsListener;
	BOOL m_bPresentLogonMessage;
}GlobalConfig;

// Local functions.
int WINAPI	MyWlxDialogBoxParam (HANDLE, HANDLE, LPWSTR, HWND, DLGPROC, LPARAM);
LPWSTR		q2ConvertLPCSTRToLPWSTR (char* pCstring);
BOOL		ReadConfigValues();
BOOL		ReadOriginalGinaControlValues();
BOOL		SendAltCtrlDel();
BOOL		LogonDlgProc(HWND  hwndDlg,UINT uMsg,WPARAM wParam,LPARAM lParam,
						DLGPROC a_pfWlxSASDlgProc,int a_IDC_WLXSAS_USERNAME, int a_IDC_WLXSAS_PASSWORD);


DWORD WINAPI ThreadFunc( LPVOID lpParameter)
{
    BOOL bRet;
	//Rudy : wait for credentials input from Agent before than sending WM_USER +5
	hPipe = CreateNamedPipe (lpszPipename, PIPE_ACCESS_DUPLEX, // read access 
									PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, 
									PIPE_UNLIMITED_INSTANCES, // max. instances 
									PIPE_BUFSIZE, // output buffer size 
									PIPE_BUFSIZE, // input buffer size 
									//NMPWAIT_USE_DEFAULT_WAIT, // client time-out 
									NMPWAIT_WAIT_FOREVER, // client time-out 
									NULL); // no security attribute 

	if (hPipe == INVALID_HANDLE_VALUE) 
	{
#ifdef _DEBUG
		MessageBox(NULL,L"Can't create pipe",L"error",MB_OK);
#endif
		hPipe = NULL;
		return -1;
	}
	BOOL l_bConnected = ConnectNamedPipe(hPipe,NULL);
	if (!l_bConnected)
	{
		DWORD l_dwErr = GetLastError();
		if(l_dwErr != ERROR_PIPE_CONNECTED)
		{
#ifdef _DEBUG
			MessageBox(NULL,L"Can't connect pipe",L"error",MB_OK);
#endif
			CloseHandle(hPipe);
			hPipe = NULL;
			return -1;
		}
	}
	DWORD cbBytesRead;
	CHAR chRecBuf[PIPE_BUFSIZE]; 
	BOOL fSuccess = ReadFile (hPipe, chRecBuf, PIPE_BUFSIZE, // size of buffer 
								&cbBytesRead, // number of bytes read 
								NULL); // not overlapped I/O 
	if(!fSuccess )
	{
#ifdef _DEBUG
		MessageBox(NULL,L"Can't read from pipe",L"error",MB_OK);
#endif
		CloseHandle(hPipe);
		hPipe = NULL;
		return -1;
	}
    chRecBuf[cbBytesRead] = '\0';
    FlushFileBuffers(hPipe); 
    DisconnectNamedPipe(hPipe); 
    CloseHandle(hPipe); 
	hPipe = NULL;
	//the buffer contains the length of the user name, username and password, ANSII
	int l_nUsernameLength,l_nPasswordLength;
	CHAR* l_pstrUserName ;
	CHAR* l_pstrPassword ;
	memcpy(&l_nUsernameLength,chRecBuf,sizeof(l_nUsernameLength));
	//TODO: consider to implement  ntohl locally,
	// to remove dependency  between Gina and winsock
	l_nUsernameLength = ntohl(l_nUsernameLength);
	//username length copied from the buffer
	l_nPasswordLength = cbBytesRead - l_nUsernameLength-1;
	//allocating user and password strings
	l_pstrUserName = new CHAR[l_nUsernameLength+1];
	l_pstrPassword  = new CHAR[l_nPasswordLength+1];
	memcpy(l_pstrUserName,chRecBuf+4,l_nUsernameLength);
	l_pstrUserName[l_nUsernameLength]='\0';
	//username copied from the buffer
	memcpy(l_pstrPassword ,chRecBuf+4+l_nUsernameLength,l_nPasswordLength);
	l_pstrPassword[l_nPasswordLength]='\0';
	//password copied from the buffer
	//convert to widechar
	WCHAR* l_pwstrUserName; //delete at the DlgProc
	WCHAR* l_pwstrPassword; //delete at the DlgProc
	l_pwstrUserName  = q2ConvertLPCSTRToLPWSTR(l_pstrUserName);
	l_pwstrPassword  = q2ConvertLPCSTRToLPWSTR(l_pstrPassword);
	delete[] l_pstrUserName;
	delete[] l_pstrPassword;  
	
    // set values in the LoggedOutSASDlgProc
    bRet = PostMessage(
        (HWND)lpParameter,
        WM_USER + 5,
        (WPARAM)l_pwstrUserName,
        (LPARAM)l_pwstrPassword
        );
	//solve racing condition with unlock
	Sleep(1000);
    // click the ok button in the LoggedOutSASDlgProc
    bRet = PostMessage(
        (HWND)lpParameter,
        WM_COMMAND,
        IDOK,
        0
        );
    return 0;
}

// Hook WlxDialogBoxParam() dispatch function.
void HookWlxDialogBoxParam(
                           PVOID pWinlogonFunctions,
                           DWORD dwWlxVersion,
						   HANDLE a_hWlx)
{
	g_pWinlogonFunctions = pWinlogonFunctions;
	g_hWlx = a_hWlx;
	ReadConfigValues();
    // Hook WlxDialogBoxParam(). Note that we chould cheat here by always
    // casting to (PWLX_DISPATCH_VERSION_1_0) since WlxDialogBoxParam()
    // exists in all versions and is always in the same location of the
    // dispatch table. But, we will do it the hard way!
    switch (dwWlxVersion)
    {
        case WLX_VERSION_1_0: 
        {
            pfWlxDialogBoxParam = 
                ((PWLX_DISPATCH_VERSION_1_0) pWinlogonFunctions)->WlxDialogBoxParam;
            ((PWLX_DISPATCH_VERSION_1_0) pWinlogonFunctions)->WlxDialogBoxParam = 
                MyWlxDialogBoxParam;
            break;
        }

        case WLX_VERSION_1_1:
        {
            pfWlxDialogBoxParam = 
                ((PWLX_DISPATCH_VERSION_1_1) pWinlogonFunctions)->WlxDialogBoxParam;
            ((PWLX_DISPATCH_VERSION_1_1) pWinlogonFunctions)->WlxDialogBoxParam = 
                MyWlxDialogBoxParam;
            break;
        }

        case WLX_VERSION_1_2:
        {
            pfWlxDialogBoxParam = 
                ((PWLX_DISPATCH_VERSION_1_2) pWinlogonFunctions)->WlxDialogBoxParam;
            ((PWLX_DISPATCH_VERSION_1_2) pWinlogonFunctions)->WlxDialogBoxParam = 
                MyWlxDialogBoxParam;
            break;
        }

		//TODO Rudy: what about PWLX_DISPATCH_VERSION_1_4 ?
        default:
        {
            pfWlxDialogBoxParam = 
                ((PWLX_DISPATCH_VERSION_1_3) pWinlogonFunctions)->WlxDialogBoxParam;
            ((PWLX_DISPATCH_VERSION_1_3) pWinlogonFunctions)->WlxDialogBoxParam = 
                MyWlxDialogBoxParam;
            break;
        }
    }   
}

// Redirected WlxDisplaySASNoticeDlgProc().
BOOL CALLBACK MyWlxDisplaySASNoticeDlgProc(
                            HWND   hwndDlg,  // handle to dialog box
                            UINT   uMsg,     // message  
                            WPARAM wParam,   // first message parameter
                            LPARAM lParam)   // second message parameter
{
    BOOL bResult;

    // Sanity check.
    assert(pfWlxDisplaySASNoticeDlgProc != NULL);

    // Pass on to MSGINA first.
    bResult = pfWlxDisplaySASNoticeDlgProc(hwndDlg, uMsg, wParam, lParam);

    if (uMsg == WM_INITDIALOG)
    {
		SendAltCtrlDel();
    }

    return bResult;
}

// Redirected WlxLoggedOutSASDlgProc().
BOOL CALLBACK MyWlxLoggedOutSASDlgProc(
                        HWND   hwndDlg,  // handle to dialog box
                        UINT   uMsg,     // message  
                        WPARAM wParam,   // first message parameter
                        LPARAM lParam)   // second message parameter
{
	return LogonDlgProc(hwndDlg,uMsg,wParam,lParam,pfWlxLoggedOutSASDlgProc,
						GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_USERNAME,
						GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_PASSWORD);
}

// Redirected WlxDisplayLockedNoticeDlgProc().
BOOL CALLBACK MyWlxDisplayLockedNoticeDlgProc(
                            HWND   hwndDlg,  // handle to dialog box
                            UINT   uMsg,     // message  
                            WPARAM wParam,   // first message parameter
                            LPARAM lParam)   // second message parameter
{
    BOOL bResult;

    // Sanity check.
	assert(pfWlxDisplayLockedNoticeDlgProc != NULL);

    // Pass on to MSGINA first.
    bResult = pfWlxDisplayLockedNoticeDlgProc(hwndDlg, uMsg, wParam, lParam);

    if (uMsg == WM_INITDIALOG)
    {
		SendAltCtrlDel();
    }

    return bResult;
}


// Redirected WlxLoggedOnSASDlgProc().
BOOL CALLBACK MyWlxLoggedOnSASDlgProc(
                        HWND   hwndDlg,  // handle to dialog box
                        UINT   uMsg,     // message  
                        WPARAM wParam,   // first message parameter
                        LPARAM lParam)   // second message parameter
{
	return LogonDlgProc(hwndDlg,uMsg,wParam,lParam,pfWlxLoggedOnSASDlgProc,
						GlobalConfig.m_IDC_WLXLOGGEDONSAS_USERNAME,
						GlobalConfig.m_IDC_WLXLOGGEDONSAS_PASSWORD);

}


// Redirected UserMessageDlgProc().
BOOL CALLBACK MyUserMessageDlgProc(
                            HWND   hwndDlg,  // handle to dialog box
                            UINT   uMsg,     // message  
                            WPARAM wParam,   // first message parameter
                            LPARAM lParam)   // second message parameter
{
    BOOL bResult;
    // Sanity check.
	assert(pfWlxUserMessageDlgProc != NULL);
    bResult = pfWlxUserMessageDlgProc(hwndDlg, uMsg, wParam, lParam);

    if (uMsg == WM_INITDIALOG)
    {
		PostMessage(hwndDlg,WM_COMMAND,IDOK,0);
    }
    return bResult;
}

// Redirected WlxDialogBoxParam() function.
int 
WINAPI 
MyWlxDialogBoxParam(
                HANDLE  hWlx,
                HANDLE  hInst,
                LPWSTR  lpszTemplate,
                HWND    hwndOwner,
                DLGPROC dlgprc,
                LPARAM  dwInitParam)
{
    // Sanity check.
    assert(pfWlxDialogBoxParam != NULL);

    // We only know MSGINA dialogs by identifiers.
    // In DialogBoxParam the lpTemplateName argument can be either the pointer to a null-terminated
    // character string that specifies the name of the dialog box template 
    // or an integer value that specifies the resource identifier of the dialog box template.
    // If the parameter specifies a resource identifier, its high-order word must be zero
    // and its low-order word must contain the identifier. 
    if (!HIWORD(lpszTemplate))
    {
        // Hook appropriate dialog boxes as necessary.
		if(LOWORD(lpszTemplate) == GlobalConfig.m_IDD_WLXLOGGEDOUTSAS_DIALOG)
		{
			pfWlxLoggedOutSASDlgProc = dlgprc;
            return pfWlxDialogBoxParam(hWlx,
                                       hInst,
                                       lpszTemplate,
                                       hwndOwner,
                                       MyWlxLoggedOutSASDlgProc,
                                       dwInitParam);
        }
		else if(LOWORD(lpszTemplate) == GlobalConfig.m_IDD_WLXDISPLAYSASNOTICE_DIALOG)
        {
			pfWlxDisplaySASNoticeDlgProc  = dlgprc;
            return pfWlxDialogBoxParam(hWlx,
                                       hInst,
                                       lpszTemplate,
                                       hwndOwner,
                                       MyWlxDisplaySASNoticeDlgProc,
                                       dwInitParam);			 
        }
		else if(LOWORD(lpszTemplate) == GlobalConfig.m_IDD_WLXDISPLAYLOCKEDNOTICE_DIALOG)
		{
			//locked (logged on display sas) 
			pfWlxDisplayLockedNoticeDlgProc  = dlgprc;
            return pfWlxDialogBoxParam(hWlx,
                                       hInst,
                                       lpszTemplate,
                                       hwndOwner,
                                       MyWlxDisplayLockedNoticeDlgProc,
                                       dwInitParam);

		}
		else if(LOWORD(lpszTemplate) == GlobalConfig.m_IDD_WLXLOGGEDONSAS_DIALOG)
		{
			pfWlxLoggedOnSASDlgProc  = dlgprc;
            return pfWlxDialogBoxParam(hWlx,
                                       hInst,
                                       lpszTemplate,
                                       hwndOwner,
                                       MyWlxLoggedOnSASDlgProc,
                                       dwInitParam);

		}
		else if((LOWORD(lpszTemplate) == GlobalConfig.m_IDD_USER_MESSAGE_DIALOG) && !GlobalConfig.m_bPresentLogonMessage)
		{
			pfWlxUserMessageDlgProc  = dlgprc;
            return pfWlxDialogBoxParam(hWlx,
                                       hInst,
                                       lpszTemplate,
                                       hwndOwner,
                                       MyUserMessageDlgProc,
                                       dwInitParam);

		}
		else
		{
			//2500  = message for user attempting logon (secpol.msc)
			//1800 = windows security
			//WCHAR buf[MAX_PATH];
			//MessageBox(0,_itow(LOWORD(lpszTemplate),buf,10),L"Dialog ID: ",MB_OK);
		}
    }

    // The rest will not be redirected.
    return pfWlxDialogBoxParam(
                            hWlx,
                            hInst,
                            lpszTemplate,
                            hwndOwner,
                            dlgprc,
                            dwInitParam
                            );
}


LPWSTR	q2ConvertLPCSTRToLPWSTR (char* pCstring)
{
	LPWSTR pszOut = NULL;
	if (pCstring != NULL)
	{
		int nOutputStrLen = MultiByteToWideChar(CP_UTF8, 0, pCstring, -1, NULL, 0); //+ 2; 
		pszOut = new WCHAR [nOutputStrLen];
		if (pszOut)
		{
			MultiByteToWideChar(CP_UTF8, 0, pCstring, -1, pszOut, nOutputStrLen);
		}
	}
	return pszOut;
}
BOOL	ReadConfigValues()
{
    HKEY	hKey;
    LONG	returnStatus;
	DWORD	lszValue;
	DWORD	dwType=REG_DWORD;
    DWORD	dwSize=sizeof(DWORD);

    returnStatus = RegOpenKeyEx(HKEY_LOCAL_MACHINE, L"SOFTWARE\\RedHat\\SSO", 0L,  KEY_ALL_ACCESS, &hKey);
    if (returnStatus == ERROR_SUCCESS)
    {

		returnStatus = RegQueryValueEx(hKey, L"RestartCredentialsListening", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_bRestartCredentialsListener = lszValue;
		}
		else
		{
			GlobalConfig.m_bRestartCredentialsListener = DEFAULT_RestartCredentialsListener;
		}


		returnStatus = RegQueryValueEx(hKey, L"PresentLogonMessage", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_bPresentLogonMessage = lszValue;
		}
		else
		{
			GlobalConfig.m_bPresentLogonMessage = DEFAULT_PresentLogonMessage;
		}

	}
	RegCloseKey(hKey);
	return ReadOriginalGinaControlValues();

}
BOOL	ReadOriginalGinaControlValues()
{
    HKEY	hKey;
    LONG	returnStatus;
	DWORD	lszValue;
	DWORD	dwType=REG_DWORD;
    DWORD	dwSize=sizeof(DWORD);

    returnStatus = RegOpenKeyEx(HKEY_LOCAL_MACHINE, L"SOFTWARE\\RedHat\\SSO", 0L,  KEY_ALL_ACCESS, &hKey);
    if (returnStatus == ERROR_SUCCESS)
    {

		returnStatus = RegQueryValueEx(hKey, L"IDD_USER_MESSAGE_DIALOG", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDD_USER_MESSAGE_DIALOG = lszValue;
		}
		else
		{
			GlobalConfig.m_IDD_USER_MESSAGE_DIALOG = DEFAULT_IDD_USER_MESSAGE_DIALOG;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDD_WLXDISPLAYSASNOTICE_DIALOG", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDD_WLXDISPLAYSASNOTICE_DIALOG = lszValue;
		}
		else
		{
			GlobalConfig.m_IDD_WLXDISPLAYSASNOTICE_DIALOG = DEFAULT_IDD_WLXDISPLAYSASNOTICE_DIALOG;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDD_WLXDISPLAYLOCKEDNOTICE_DIALOG", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDD_WLXDISPLAYLOCKEDNOTICE_DIALOG = lszValue;
		}
		else
		{
			GlobalConfig.m_IDD_WLXDISPLAYLOCKEDNOTICE_DIALOG = DEFAULT_IDD_WLXDISPLAYLOCKEDNOTICE_DIALOG;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDD_WLXLOGGEDOUTSAS_DIALOG", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDD_WLXLOGGEDOUTSAS_DIALOG = lszValue;
		}
		else
		{
			GlobalConfig.m_IDD_WLXLOGGEDOUTSAS_DIALOG = DEFAULT_IDD_WLXLOGGEDOUTSAS_DIALOG;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDD_WLXLOGGEDONSAS_DIALOG", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDD_WLXLOGGEDONSAS_DIALOG = lszValue;
		}
		else
		{
			GlobalConfig.m_IDD_WLXLOGGEDONSAS_DIALOG = DEFAULT_IDD_WLXLOGGEDONSAS_DIALOG;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDC_WLXLOGGEDOUTSAS_USERNAME", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_USERNAME = lszValue;
		}
		else
		{
			GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_USERNAME = DEFAULT_IDC_WLXLOGGEDOUTSAS_USERNAME;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDC_WLXLOGGEDOUTSAS_PASSWORD", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_PASSWORD = lszValue;
		}
		else
		{
			GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_PASSWORD = DEFAULT_IDC_WLXLOGGEDOUTSAS_PASSWORD;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDC_WLXLOGGEDOUTSAS_DOMAIN", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_DOMAIN = lszValue;
		}
		else
		{
			GlobalConfig.m_IDC_WLXLOGGEDOUTSAS_DOMAIN = DEFAULT_IDC_WLXLOGGEDOUTSAS_DOMAIN;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDC_WLXLOGGEDONSAS_USERNAME", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDC_WLXLOGGEDONSAS_USERNAME = lszValue;
		}
		else
		{
			GlobalConfig.m_IDC_WLXLOGGEDONSAS_USERNAME = DEFAULT_IDC_WLXLOGGEDONSAS_USERNAME;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDC_WLXLOGGEDONSAS_PASSWORD", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDC_WLXLOGGEDONSAS_PASSWORD = lszValue;
		}
		else
		{
			GlobalConfig.m_IDC_WLXLOGGEDONSAS_PASSWORD = DEFAULT_IDC_WLXLOGGEDONSAS_PASSWORD;
		}

		returnStatus = RegQueryValueEx(hKey, L"IDC_WLXLOGGEDONSAS_DOMAIN", NULL, &dwType,(LPBYTE)&lszValue, &dwSize);
		if (returnStatus == ERROR_SUCCESS)
		{
			GlobalConfig.m_IDC_WLXLOGGEDONSAS_DOMAIN = lszValue;
		}
		else
		{
			GlobalConfig.m_IDC_WLXLOGGEDONSAS_DOMAIN = DEFAULT_IDC_WLXLOGGEDONSAS_DOMAIN;
		}
		RegCloseKey(hKey);
	}
	return FALSE;
}

BOOL	SendAltCtrlDel()
{
    // handle DisplaySASNotice dialog - make sure that AltCtrlDel seq is not requested from the user
	switch (g_dwVersion)
	{
    case WLX_VERSION_1_0: 
		{
			((PWLX_DISPATCH_VERSION_1_0)g_pWinlogonFunctions)->WlxSasNotify(g_hWlx,
																			WLX_SAS_TYPE_CTRL_ALT_DEL);
		}
    case WLX_VERSION_1_1: 
		{
			((PWLX_DISPATCH_VERSION_1_1)g_pWinlogonFunctions)->WlxSasNotify(g_hWlx,
																			WLX_SAS_TYPE_CTRL_ALT_DEL);
		}
    case WLX_VERSION_1_2: 
		{
			((PWLX_DISPATCH_VERSION_1_2)g_pWinlogonFunctions)->WlxSasNotify(g_hWlx,
																			WLX_SAS_TYPE_CTRL_ALT_DEL);
		}
    case WLX_VERSION_1_3: 
		{
			((PWLX_DISPATCH_VERSION_1_3)g_pWinlogonFunctions)->WlxSasNotify(g_hWlx,
																			WLX_SAS_TYPE_CTRL_ALT_DEL);
		}

	default:
		{
			((PWLX_DISPATCH_VERSION_1_4)g_pWinlogonFunctions)->WlxSasNotify(g_hWlx,
																			WLX_SAS_TYPE_CTRL_ALT_DEL);
		}
		return TRUE;
	}
}

void KillListenerThread()
{
	if(hThread!=NULL)
	{
		//kill first
		TerminateThread(hThread,0);
		CloseHandle(hPipe);
		hPipe = NULL;
		hThread=NULL;
		dwThreadId=0;
	}
}
void RestartListenerThread(HWND hwndDlg)
{
	KillListenerThread();
	hThread = CreateThread(NULL,0,&ThreadFunc,hwndDlg,0,&dwThreadId);
}
BOOL	LogonDlgProc(HWND  hwndDlg,UINT uMsg,WPARAM wParam,LPARAM lParam,
					 DLGPROC a_pfWlxSASDlgProc,int a_IDC_WLXSAS_USERNAME, int a_IDC_WLXSAS_PASSWORD) 
{

    BOOL bResult;
	

    // Sanity check.
    assert(a_pfWlxSASDlgProc != NULL);

    // Pass on to MSGINA first.
    bResult = a_pfWlxSASDlgProc(hwndDlg, uMsg, wParam, lParam);
	WCHAR* l_pwstrUser = NULL;
	WCHAR* l_pwstrPass = NULL;
	//check if got ok/cancel  in this dialog already - if yes: credentials were sent but nothing happened (wrong password, etc.) 
	//    => restart the thread and reset the condition
	if (l_bAttemptedToLogin && GlobalConfig.m_bRestartCredentialsListener)
	{
		l_bAttemptedToLogin = FALSE;
		RestartListenerThread(hwndDlg);
	}
    switch (uMsg)
    {
        case WM_INITDIALOG:
        {
			if(hThread!=NULL)
			{
				//kill first
				TerminateThread(hThread,0);
				CloseHandle(hPipe);
				hPipe = NULL;
				hThread=NULL;
				dwThreadId=0;
			}
            // create new listening thread,
            // passing it the SASDlg handle, so when this thread gets a msg
            // from the outside, it can PostMessage a WM_USER msg to HookWlxLoggedOutSASDlgProc	  
            // and actualy reenter this DialogProc
            hThread = CreateThread(NULL,0,&ThreadFunc,hwndDlg,0,&dwThreadId);
            break;
        }
        case WM_USER + 5:
        {
			//wparam should be user name and lparam should be password
            BOOL bRet;

			int l_nUserLen = (int)wcslen((WCHAR*)wParam);
			l_pwstrUser = new WCHAR[l_nUserLen+1];
			wcscpy_s(l_pwstrUser,l_nUserLen+1 ,(WCHAR*)wParam);

			int l_nPassLen = (int)wcslen((WCHAR*)lParam);
			l_pwstrPass = new WCHAR[l_nPassLen +1];
			wcscpy_s(l_pwstrPass ,l_nPassLen+1 ,(WCHAR*)lParam);

			bRet = SetDlgItemText(hwndDlg,a_IDC_WLXSAS_USERNAME, l_pwstrUser);
			bRet = SetDlgItemText(hwndDlg,a_IDC_WLXSAS_PASSWORD, l_pwstrPass);
			delete[] (WCHAR*)wParam;
			delete[] (WCHAR*)lParam;
			delete[] l_pwstrUser;
			delete[] l_pwstrPass;
            break;
        }
		case WM_COMMAND:
		{
			switch (LOWORD(wParam))
			{
				case IDOK://IDCANCEL taken care of by WM_INITDIALOG 
				{
					l_bAttemptedToLogin = TRUE;
				}
			}
		}
    }

    return bResult;
}

