# sr_suite_utilities installer
OutFile "${OUTFILE}"

Var MAYA_INSTALL_LOCATION
Var MAYA_SCRIPT_LOCATION

RequestExecutionLevel admin



# First section?
Section

    # call UserInfo plugin to get user info.  The plugin puts the result in the stack
    MessageBox MB_OK "Preparing to install .py modules for Shaper Rigs Suite Utilities"

    # Get account type (Admin or not) and pop it from $0, then jump three if not matching Admin.
    UserInfo::getAccountType
    Pop $0
    StrCmp $0 "Admin" +3

    MessageBox MB_OK "Must be run as administrator."
    Return

    # Begin proper execution if admin?


    # define uninstaller name
    WriteUninstaller $INSTDIR\srsu_uninstaller.exe

SectionEnd


Section "Uninstall"
    
    # Always delete uninstaller first
    Delete $INSTDIR\uninstaller.exe
 
    # now delete installed file
    Delete $INSTDIR\test.txt
 
    # Delete the directory
    RMDir $INSTDIR

SectionEnd

