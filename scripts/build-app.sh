# Clean existing build and packaging directories
rm -rf build dist


# Package new application
python setup.py2app.py py2app | grep -v copying | grep -v creating | grep -v byte-compiling | grep -v strip

echo
echo "Copy data files"

# Copy data files
cp -rv /opt/local/lib/Resources/qt_menu.nib \
	dist/Puzzlebox\ Brainstorms.app/Contents/Resources/

echo
echo "Copy images"

cp -rv images \
	dist/Puzzlebox\ Brainstorms.app/Contents/Resources


echo
echo "Configure qt.conf"

# Avoid error in which Qt libraries are loaded twice
# and configure library paths for Qt image PlugIns
echo '[Paths]' > dist/Puzzlebox\ Brainstorms.app/Contents/Resources/qt.conf
echo '  Plugins=PlugIns' >> dist/Puzzlebox\ Brainstorms.app/Contents/Resources/qt.conf


echo
echo "Copy plugins"

mkdir dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns
cp -rv /opt/local/share/qt4/plugins/imageformats dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns

#find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec otool -L {} \;

echo
echo "Update plugins permissions"

find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec install_name_tool -change /opt/local/lib/libQtGui.4.dylib @executable_path/../Frameworks/libQtGui.4.dylib {} \;
find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec install_name_tool -change /opt/local/lib/libQtCore.4.dylib @executable_path/../Frameworks/libQtCore.4.dylib {} \;
find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec install_name_tool -change /opt/local/lib/libQtXml.4.dylib @executable_path/../Frameworks/libQtXml.4.dylib {} \;
find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec install_name_tool -change /opt/local/lib/libQtSvg.4.dylib @executable_path/../Frameworks/libQtSvg.4.dylib {} \;
find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec install_name_tool -change /opt/local/lib/libjpeg.8.dylib @executable_path/../Frameworks/libjpeg.8.dylib {} \;
find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec install_name_tool -change /opt/local/lib/libmng.1.dylib @executable_path/../Frameworks/libmng.1.dylib {} \;
find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec install_name_tool -change /opt/local/lib/libtiff.3.dylib @executable_path/../Frameworks/libtiff.3.dylib {} \;

find dist/Puzzlebox\ Brainstorms.app/Contents/PlugIns -type f -exec otool -L {} \; | grep opt

