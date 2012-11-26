========================================================================
    DYNAMIC LINK LIBRARY : GinaSSO Project Overview
========================================================================

How to install GinaSSO
=======================

1) Copy GinaSSO.dll to %SystemRoot%\System32 directory.
2) Run RegEdit
3) Create the following value under
   HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Winlogon.
   Value Name: GinaDLL
   Value Type: REG_SZ
   Value Data: "GinaSSO.dll"
4) Exit RegEdit.
5) Reboot.
