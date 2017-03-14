; Puzzlebox Brainstorms Windows Installer

; NOTE: this .NSI script is designed for NSIS v1.8+

Name "Puzzlebox Brainstorms"
OutFile "Puzzlebox-Brainstorms-0.8.4-setup.exe"

; Some default compiler settings (uncomment and change at will):
; SetCompress auto ; (can be off or force)
; SetDatablockOptimize on ; (can be off)
; CRCCheck on ; (can be off)
; AutoCloseWindow false ; (can be true for the window go away automatically at end)
; ShowInstDetails hide ; (can be show to have them shown, or nevershow to disable)
; SetDateSave off ; (can be on to have files restored to their orginal date)

LicenseText "You must agree to this license before installing."
LicenseData "LICENSE.txt"

InstallDir "$PROGRAMFILES\Puzzlebox Brainstorms"
InstallDirRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Puzzlebox Brainstorms\Puzzlebox Brainstorms" ""
;DirShow show ; (make this hide to not let the user change it)
DirText "Select the directory to install Puzzlebox Brainstorms into:"

InstallColors /windows

Section "" ; (default section)
SetOutPath "$INSTDIR"
; add files / whatever that need to be installed here.
WriteRegStr HKEY_LOCAL_MACHINE "SOFTWARE\Puzzlebox Brainstorms\Puzzlebox Brainstorms" "" "$INSTDIR"
WriteRegStr HKEY_LOCAL_MACHINE "Software\Microsoft\Windows\CurrentVersion\Uninstall\Puzzlebox Brainstorms\Puzzlebox Brainstorms" "DisplayName" "Puzzlebox Brainstorms (remove only)"
WriteRegStr HKEY_LOCAL_MACHINE "Software\Microsoft\Windows\CurrentVersion\Uninstall\Puzzlebox Brainstorms\Puzzlebox Brainstorms" "UninstallString" '"$INSTDIR\PuzzlesboxBrainstorms-Uninstall.exe"'

 File dist\brainstorms-local.exe
; File dist\brainstorms-network.exe
; File dist\msvcr71.dll
; File dist\python25.dll
; File dist\w9xpopen.exe
 File puzzlebox_brainstorms_configuration.ini

 File dist\python27.dll

 File dist\bz2.pyd
 File dist\_ctypes.pyd
 File dist\_hashlib.pyd
; File dist\phonon4.dll
 File dist\pyside-python2.7.dll
 File dist\PySide.QtCore.pyd
 File dist\PySide.QtGui.pyd
 File dist\PySide.QtNetwork.pyd
 File dist\PySide.QtSvg.pyd
; File dist\PySide.QtWebKit.pyd
 File dist\python27.dll
 File dist\QtCore4.dll
 File dist\QtGui4.dll
 File dist\QtNetwork4.dll
; File dist\QtWebKit4.dll
 File dist\select.pyd
 File dist\shiboken-python2.7.dll
 File dist\_socket.pyd
 File dist\_ssl.pyd
 File dist\unicodedata.pyd

; File dist\LIBEAY32.dll
 File dist\pyexpat.pyd
; File dist\PyQt4.QtCore.pyd
; File dist\PyQt4.QtGui.pyd
; File dist\PyQt4.QtNetwork.pyd
; File dist\PyQt4.QtWebKit.pyd
 File dist\pywintypes27.dll
; File dist\sip.pyd
; File dist\SSLEAY32.dll
; File dist\tcl85.dll
; File dist\tk85.dll
; File dist\_tkinter.pyd
 File dist\win32api.pyd
; File dist\win32pdh.pyd
 File dist\win32pipe.pyd

SetOutPath $INSTDIR\docs
 File LICENSE.txt

 File docs\readme.txt

SetOutPath $INSTDIR\emokey
 File emokey\puzzlebox_brainstorms.ekm
 File emokey\puzzlebox_brainstorms-wheelchair.ekm

SetOutPath $INSTDIR\emoscript
 File emoscript\puzzlebox_brainstorms-test_drive-push_pull.emo
 File emoscript\puzzlebox_brainstorms-training-pull.emo
 File emoscript\puzzlebox_brainstorms-training-push.emo

SetOutPath $INSTDIR\images
 File images\1-upper_left-orange.png
 File images\1-upper_left-white.png
 File images\2-up-orange.png
 File images\2-up-white.png
 File images\3-upper_right-orange.png
 File images\3-upper_right-white.png
 File images\7-lower_left-orange.png
 File images\7-lower_left-white.png
 File images\8-down-orange.png
 File images\8-down-white.png
 File images\9-lower_right-orange.png
 File images\9-lower_right-white.png
 File images\puzzlebox.ico
 File images\puzzlebox_logo.png
 File images\brainstorms-aileron_left.svg
 File images\brainstorms-aileron_right.svg
 File images\brainstorms-elevator_forward.svg
 File images\brainstorms-elevator_reverse.svg
 File images\brainstorms-fly_forward.svg
 File images\brainstorms-hover.svg
 File images\brainstorms-land_arrow.svg
 File images\brainstorms-rudder-left.svg
 File images\brainstorms-rudder-right.svg
 File images\brainstorms_stop.svg
 File images\brainstorms_wheelchair_forward.svg
 File images\brainstorms_wheelchair_left.svg
 File images\brainstorms_wheelchair_reverse.svg
 File images\brainstorms_wheelchair_right.svg
 File images\braintorms-throttle_up.svg
 File images\puzzlebox_helicopter.svg
 File images\brainstorms-aileron_left.png
 File images\brainstorms-aileron_right.png
 File images\brainstorms-elevator_forward.png
 File images\brainstorms-elevator_reverse.png
 File images\brainstorms-fly_forward.png
 File images\brainstorms-hover.png
 File images\brainstorms-land_arrow.png
 File images\brainstorms-rudder-left.png
 File images\brainstorms-rudder-right.png
 File images\brainstorms_stop.png
 File images\brainstorms_wheelchair_forward.png
 File images\brainstorms_wheelchair_left.png
 File images\brainstorms_wheelchair_reverse.png
 File images\brainstorms_wheelchair_right.png
 File images\braintorms-throttle_up.png
 File images\puzzlebox_helicopter.png


SetOutPath $INSTDIR\imageformats
 File packaging\win32\imageformats\qgif4.dll
 File packaging\win32\imageformats\qico4.dll
 File packaging\win32\imageformats\qjpeg4.dll
 File packaging\win32\imageformats\qmng4.dll
 File packaging\win32\imageformats\qsvg4.dll
 File packaging\win32\imageformats\qtiff4.dll

;SetOutPath $INSTDIR\lib
; File dist\lib\library.zip

;SetOutPath $INSTDIR\fonts
; File dist\fonts\tahomabd.ttf
; File dist\fonts\tahoma.ttf

;SetOutPath $INSTDIR\package
; File package\vcredist_x86.exe
;
;ExecWait 'package\Vcredist_x86.exe /q:a /c:"msiexec /i vcredist.msi /qn /l*v %temp%\vcredist_x86.log"'

SetOutPath $INSTDIR\package
 File packaging\win32\vcredist_x86.exe

ExecWait '"$INSTDIR\package\vcredist_x86.exe" /q:a /c:"msiexec /i vcredist.msi /qn /l*v %temp%\vcredist_x86.log"'


; write out uninstaller
WriteUninstaller "$INSTDIR\PuzzleboxBrainstorms-Uninstall.exe"

SectionEnd ; end of default section


Section "Start Menu + Desktop Icons"
;  SetOutPath "$SMPROGRAMS\Puzzlebox Brainstorms"
  SetOutPath $INSTDIR
  CreateDirectory "$SMPROGRAMS\Puzzlebox Brainstorms"
  CreateShortCut "$SMPROGRAMS\Puzzlebox Brainstorms\Puzzlebox Brainstorms.lnk" \
                 "$INSTDIR\brainstorms-local.exe" \
                 ""  "$INSTDIR\images\puzzlebox.ico"  "0"  ""
  CreateShortCut "$SMPROGRAMS\Puzzlebox Brainstorms\Edit Puzzlebox Brainstorms Configuration.lnk" \
                 "$INSTDIR\puzzlebox_brainstorms_configuration.ini" \
                 ""  ""  "0"  ""
  CreateShortCut "$SMPROGRAMS\Puzzlebox Brainstorms\Uninstall Puzzlebox Brainstorms.lnk" \
                 "$INSTDIR\PuzzleboxBrainstorms-Uninstall.exe"
  CreateShortCut "$DESKTOP\Puzzlebox Brainstorms.lnk" \
                 "$INSTDIR\brainstorms-local.exe" \
                 ""  "$INSTDIR\images\puzzlebox.ico"  "0"  ""
SectionEnd


; begin uninstall settings/section
UninstallText "This will uninstall Puzzlebox Brainstorms from your system"

Section Uninstall
; add delete commands to delete whatever files/registry keys/etc you installed here.
 Delete "$SMPROGRAMS\Puzzlebox Brainstorms\Puzzlebox Brainstorms.lnk"
 Delete "$SMPROGRAMS\Puzzlebox Brainstorms\Edit Puzzlebox Brainstorms Configuration.lnk" 
 Delete "$SMPROGRAMS\Puzzlebox Brainstorms\Uninstall Puzzlebox Brainstorms.lnk" 
  RMDir "$SMPROGRAMS\Puzzlebox Brainstorms"
 Delete "$DESKTOP\Puzzlebox Brainstorms.lnk"


 Delete $INSTDIR\brainstorms-local.exe
; Delete $INSTDIR\brainstorms-network.exe
; Delete $INSTDIR\msvcr71.dll
; Delete $INSTDIR\python25.dll
; Delete $INSTDIR\w9xpopen.exe
 Delete $INSTDIR\puzzlebox_brainstorms_configuration.ini

 Delete $INSTDIR\bz2.pyd
 Delete $INSTDIR\_ctypes.pyd
 Delete $INSTDIR\_hashlib.pyd
; Delete $INSTDIR\phonon4.dll
 Delete $INSTDIR\pyside-python2.7.dll
 Delete $INSTDIR\PySide.QtCore.pyd
 Delete $INSTDIR\PySide.QtGui.pyd
 Delete $INSTDIR\PySide.QtNetwork.pyd
 Delete $INSTDIR\PySide.QtSvg.pyd
; Delete $INSTDIR\PySide.QtWebKit.pyd
 Delete $INSTDIR\python27.dll
 Delete $INSTDIR\QtCore4.dll
 Delete $INSTDIR\QtGui4.dll
 Delete $INSTDIR\QtNetwork4.dll
; Delete $INSTDIR\QtWebKit4.dll
 Delete $INSTDIR\select.pyd
 Delete $INSTDIR\shiboken-python2.7.dll
 Delete $INSTDIR\_socket.pyd
 Delete $INSTDIR\_ssl.pyd
 Delete $INSTDIR\unicodedata.pyd

; Delete $INSTDIR\LIBEAY32.dll
 Delete $INSTDIR\pyexpat.pyd
; Delete $INSTDIR\PyQt4.QtCore.pyd
; Delete $INSTDIR\PyQt4.QtGui.pyd
; Delete $INSTDIR\PyQt4.QtNetwork.pyd
; Delete $INSTDIR\PyQt4.QtWebKit.pyd
 Delete $INSTDIR\pywintypes27.dll
; Delete $INSTDIR\sip.pyd
; Delete $INSTDIR\SSLEAY32.dll
; Delete $INSTDIR\tcl85.dll
; Delete $INSTDIR\tk85.dll
; Delete $INSTDIR\_tkinter.pyd
 Delete $INSTDIR\win32api.pyd
; Delete $INSTDIR\win32pdh.pyd
 Delete $INSTDIR\win32pipe.pyd

 Delete $INSTDIR\docs\LICENSE.txt
 Delete $INSTDIR\docs\readme.txt
  RMDir $INSTDIR\docs


 Delete $INSTDIR\emokey\puzzlebox_brainstorms.ekm
 Delete $INSTDIR\emokey\puzzlebox_brainstorms-wheelchair.ekm
 Delete $INSTDIR\emoscript\puzzlebox_brainstorms-test_drive-push_pull.emo
 Delete $INSTDIR\emoscript\puzzlebox_brainstorms-training-pull.emo
 Delete $INSTDIR\emoscript\puzzlebox_brainstorms-training-push.emo
  RMDir $INSTDIR\emokey
  RMDir $INSTDIR\emoscript

 Delete $INSTDIR\images\1-upper_left-orange.png
 Delete $INSTDIR\images\1-upper_left-white.png
 Delete $INSTDIR\images\2-up-orange.png
 Delete $INSTDIR\images\2-up-white.png
 Delete $INSTDIR\images\3-upper_right-orange.png
 Delete $INSTDIR\images\3-upper_right-white.png
 Delete $INSTDIR\images\7-lower_left-orange.png
 Delete $INSTDIR\images\7-lower_left-white.png
 Delete $INSTDIR\images\8-down-orange.png
 Delete $INSTDIR\images\8-down-white.png
 Delete $INSTDIR\images\9-lower_right-orange.png
 Delete $INSTDIR\images\9-lower_right-white.png
 Delete $INSTDIR\images\puzzlebox.ico
 Delete $INSTDIR\images\puzzlebox_logo.png
 Delete $INSTDIR\images\brainstorms-aileron_left.svg
 Delete $INSTDIR\images\brainstorms-aileron_right.svg
 Delete $INSTDIR\images\brainstorms-elevator_forward.svg
 Delete $INSTDIR\images\brainstorms-elevator_reverse.svg
 Delete $INSTDIR\images\brainstorms-fly_forward.svg
 Delete $INSTDIR\images\brainstorms-hover.svg
 Delete $INSTDIR\images\brainstorms-land_arrow.svg
 Delete $INSTDIR\images\brainstorms-rudder-left.svg
 Delete $INSTDIR\images\brainstorms-rudder-right.svg
 Delete $INSTDIR\images\brainstorms_stop.svg
 Delete $INSTDIR\images\brainstorms_wheelchair_forward.svg
 Delete $INSTDIR\images\brainstorms_wheelchair_left.svg
 Delete $INSTDIR\images\brainstorms_wheelchair_reverse.svg
 Delete $INSTDIR\images\brainstorms_wheelchair_right.svg
 Delete $INSTDIR\images\braintorms-throttle_up.svg
 Delete $INSTDIR\images\puzzlebox_helicopter.svg
 Delete $INSTDIR\images\brainstorms-aileron_left.png
 Delete $INSTDIR\images\brainstorms-aileron_right.png
 Delete $INSTDIR\images\brainstorms-elevator_forward.png
 Delete $INSTDIR\images\brainstorms-elevator_reverse.png
 Delete $INSTDIR\images\brainstorms-fly_forward.png
 Delete $INSTDIR\images\brainstorms-hover.png
 Delete $INSTDIR\images\brainstorms-land_arrow.png
 Delete $INSTDIR\images\brainstorms-rudder-left.png
 Delete $INSTDIR\images\brainstorms-rudder-right.png
 Delete $INSTDIR\images\brainstorms_stop.png
 Delete $INSTDIR\images\brainstorms_wheelchair_forward.png
 Delete $INSTDIR\images\brainstorms_wheelchair_left.png
 Delete $INSTDIR\images\brainstorms_wheelchair_reverse.png
 Delete $INSTDIR\images\brainstorms_wheelchair_right.png
 Delete $INSTDIR\images\braintorms-throttle_up.png
 Delete $INSTDIR\images\puzzlebox_helicopter.png
  RMDir $INSTDIR\images

 Delete $INSTDIR\imageformats\qgif4.dll
 Delete $INSTDIR\imageformats\qico4.dll
 Delete $INSTDIR\imageformats\qjpeg4.dll
 Delete $INSTDIR\imageformats\qmng4.dll
 Delete $INSTDIR\imageformats\qsvg4.dll
 Delete $INSTDIR\imageformats\qtiff4.dll
  RMDir $INSTDIR\imageformats

; Delete $INSTDIR\fonts\tahomabd.ttf
; Delete $INSTDIR\fonts\tahoma.ttf
; RMDir $INSTDIR\fonts

 Delete $INSTDIR\lib\library.zip
 RMDir $INSTDIR\lib

 Delete $INSTDIR\package\vcredist_x86.exe
  RMDir $INSTDIR\package

; RMDIR $INSTDIR

Delete "$INSTDIR\PuzzleboxBrainstorms-Uninstall.exe"
DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Puzzlebox Brainstorms\Puzzlebox Brainstorms"
DeleteRegKey HKEY_LOCAL_MACHINE "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Puzzlebox Brainstorms"
;RMDir "$INSTDIR"


 RMDIR $INSTDIR


  ; if $INSTDIR was removed, skip these next ones
  IfFileExists $INSTDIR 0 Removed 
    MessageBox MB_YESNO|MB_ICONQUESTION \
      "Remove all files in your Puzzlebox Brainstorms directory? (If you have anything \
you created that you want to keep, click No)" IDNO Removed
    Delete $INSTDIR\*.* ; this would be skipped if the user hits no
    RMDir /r $INSTDIR
    IfFileExists $INSTDIR 0 Removed 
      MessageBox MB_OK|MB_ICONEXCLAMATION \
                 "Note: $INSTDIR could not be removed."
  Removed:


SectionEnd ; end of uninstall section

; eof

