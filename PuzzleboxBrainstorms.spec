# -*- mode: python -*-

imageformatsTree = Tree("packaging\\win32\\imageformats", "imageformats", [".svn"])

imagesTree = Tree('images', 'images', ['.svn'])

a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'synapse-gui.py'],
             pathex=['C:\\Development\\synapse\\trunk'])
pyz = PYZ(a.pure)

#for each in imageformatsTree:
#	each[2] = 'BINARY'

#a.binaries += [("imageformats\\qgif4.dll", "packaging\\win32\\imageformats", 'BINARY')]
#a.binaries += [("imageformats\\qico4.dll", "packaging\\win32\\imageformats", 'BINARY')]
#a.binaries += [("imageformats\\qjpeg4.dll", "packaging\\win32\\imageformats", 'BINARY')]
#a.binaries += [("imageformats\\qmng4.dll", "packaging\\win32\\imageformats", 'BINARY')]
#a.binaries += [("imageformats\\qsvg4.dll", "packaging\\win32\\imageformats", 'BINARY')]
#a.binaries += [("imageformats\\qtiff4.dll", "packaging\\win32\\imageformats", 'BINARY')]
a.binaries += imageformatsTree
print a.binaries

a.datas += imagesTree
print a.datas

exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=os.path.join('dist', 'PuzzleboxSynapse.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=False , icon='images\\puzzlebox.ico')

app = BUNDLE(exe,
             name=os.path.join('dist', 'PuzzleboxSynapse.exe.app'))

