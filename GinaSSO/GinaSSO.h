// The following ifdef block is the standard way of creating macros which make exporting 
// from a DLL simpler. All files within this DLL are compiled with the GINASSO_EXPORTS
// symbol defined on the command line. this symbol should not be defined on any project
// that uses this DLL. This way any other project whose source files include this file see 
// GINASSO_API functions as being imported from a DLL, whereas this DLL sees symbols
// defined with this macro as being exported.
#ifdef GINASSO_EXPORTS
#define GINASSO_API __declspec(dllexport)
#else
#define GINASSO_API __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

/*++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

 THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
 EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A PARTICULAR PURPOSE.

 Copyright (C) 1996 - 2000.  Microsoft Corporation.  All rights reserved.

 Module:   Ginahook.h

 Abstract: See ReadMe.txt for more detail information about this sample.

 Revision: August 6, 1999.

------------------------------------------------------------------------------*/

//
// Function prototypes for the GINA interface.
//

typedef BOOL (WINAPI * PFWLXNEGOTIATE)  (DWORD, DWORD *);
typedef BOOL (WINAPI * PFWLXINITIALIZE) (LPWSTR, HANDLE, PVOID, PVOID, PVOID *);
typedef VOID (WINAPI * PFWLXDISPLAYSASNOTICE) (PVOID);
typedef int  (WINAPI * PFWLXLOGGEDOUTSAS) (PVOID, DWORD, PLUID, PSID, PDWORD,
                                           PHANDLE, PWLX_MPR_NOTIFY_INFO, 
                                           PVOID *);
typedef BOOL (WINAPI * PFWLXACTIVATEUSERSHELL) (PVOID, PWSTR, PWSTR, PVOID);
typedef int  (WINAPI * PFWLXLOGGEDONSAS) (PVOID, DWORD, PVOID);
typedef VOID (WINAPI * PFWLXDISPLAYLOCKEDNOTICE) (PVOID);
typedef int  (WINAPI * PFWLXWKSTALOCKEDSAS) (PVOID, DWORD);
typedef BOOL (WINAPI * PFWLXISLOCKOK) (PVOID);
typedef BOOL (WINAPI * PFWLXISLOGOFFOK) (PVOID);
typedef VOID (WINAPI * PFWLXLOGOFF) (PVOID);
typedef VOID (WINAPI * PFWLXSHUTDOWN) (PVOID, DWORD);

//
// New for version 1.1
//

typedef BOOL (WINAPI * PFWLXSCREENSAVERNOTIFY) (PVOID, BOOL *);
typedef BOOL (WINAPI * PFWLXSTARTAPPLICATION) (PVOID, PWSTR, PVOID, PWSTR);

//
// New for version 1.3
//

typedef BOOL (WINAPI * PFWLXNETWORKPROVIDERLOAD) (PVOID, PWLX_MPR_NOTIFY_INFO);
typedef BOOL (WINAPI * PFWLXDISPLAYSTATUSMESSAGE) (PVOID, HDESK, DWORD, PWSTR, PWSTR);
typedef BOOL (WINAPI * PFWLXGETSTATUSMESSAGE) (PVOID, DWORD *, PWSTR, DWORD);
typedef BOOL (WINAPI * PFWLXREMOVESTATUSMESSAGE) (PVOID);

// New for version 1.4 added by Itai Shaham, 21/08/07 to support TC connections
// get prototypes from ...\Microsoft Platform SDK\Include\winwlx.h
typedef BOOL (WINAPI * PFWLXGETCONSOLESWITCHCREDENTIALS) (PVOID, PVOID);
typedef VOID (WINAPI * PFWLXRECONNECTNOTIFY) (PVOID);
typedef VOID (WINAPI * PFWLXDISCONNECTNOTIFY) (PVOID);

#ifdef __cplusplus
}
#endif // __cplusplus
