rem cx_Freeze
xcopy images dist\images /I /Y
xcopy packaging\win32\imageformats dist\imageformats /I /Y
xcopy puzzlebox_brainstorms_configuration.ini dist /I /Y

rem ***Output to Console for Debugging
\Python27\Scripts\cxfreeze brainstorms-local.py --compress --target-dir dist --base-name Console --include-modules PySide.QtNetwork,serial.win32 --icon=images\puzzlebox.ico

rem ***GUI Mode only for Distribution
rem \Python27\Scripts\cxfreeze brainstorms-local.py --compress --target-dir dist --base-name Win32GUI --include-modules PySide.QtNetwork,serial.win32 --icon=images\puzzlebox.ico


rem PyInstaller
rem \Python27\python.exe \Development\pyinstaller-1.5.1\Makespec.py --onefile --windowed --icon=images\puzzlebox.ico --name=PuzzleboxBrainstorms brainstorms-local.py

rem \Python27\python.exe \Development\pyinstaller-1.5.1\Build.py PuzzleboxBrainstorms.spec
