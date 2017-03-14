#!/usr/bin/env python
#
# Puzzlebox - Brainstorms - Distutils
#
# Copyright Puzzlebox Productions, LLC (2010-2012)
#
# This code is released under the GNU Pulic License (GPL) version 2
# For more information please refer to http://www.gnu.org/copyleft/gpl.html
#
# Last Update: 2012.08.20
#
#####################################################################

from distutils.core import setup
import os, sys
import glob

if (sys.platform == 'win32'):
	import py2exe
	import shutil
#	import matplotlib

#####################################################################
# Main
#####################################################################

if __name__ != '__main__':

	sys.exit()


##dllList = ( \
###          'mfc90.dll', \
###	   'msvcp90.dll', \
###	   'qtnetwork.pyd', \
###	   'qtxmlpatterns4.dll', \
##	   'qsvg4.dll', \
###	   'qsvgd4.dll', \
##	   'qsvgicon4.dll', \
##	   'QtSvg4.dll')
#origIsSystemDLL = py2exe.build_exe.isSystemDLL
#def isSystemDLL(pathname):
#	#print os.path.basename(pathname).lower()
#	if os.path.basename(pathname).lower() in dllList:
#		return 0
#	return origIsSystemDLL(pathname)
#py2exe.build_exe.isSystemDLL = isSystemDLL

if (sys.platform == 'win32'):
	
	# Remove the build folder, a bit slower but ensures that build contains the latest
	shutil.rmtree("build", ignore_errors=True)
	
	options={"py2exe": { \
	            "includes": [ \
	               "sip", \
	               "PySide.QtSvg", \
                       #"PyQt4._qt", \
#	               "numpy", "pylab", \
#	               "matplotlib", \
#	               "matplotlib.backends", \
#	               "matplotlib.backends.backend_qt4agg", \
#	               "matplotlib.figure", \
#	               "matplotlib.numerix.fft", \
#	               "matplotlib.numerix.linear_algebra", \
#	               "matplotlib.numerix.random_array", \
#	               "matplotlib.backends.backend_tkagg", \
#	               "PyQt4.QtSvg", \
	            ], \
#                    "dllList": [ \
#                       "qsvgicon4.dll"], \
	            "excludes": [ \
	               "bluetooth", "tcl", \
	               '_gtkagg', '_tkagg', '_agg2', \
	               '_cairo', '_cocoaagg', \
	               '_fltkagg', '_gtk', '_gtkcairo'], \
	            "dll_excludes": [ \
	               'tcl84.dll', 'tk84.dll' \
	               'libgdk-win32-2.0-0.dll',
	               'libgobject-2.0-0.dll'], \
	            #"packages": ["pytz"], \
	            "compressed": 2, \
	            "optimize": 2, \
	            "bundle_files": 2, \
	            "dist_dir": "dist", \
	            "xref": False, \
	            "skip_archive": False, \
	         }
	}
	
	data_files=[(".", \
	               ["puzzlebox_brainstorms_configuration.ini"]),
	            ("images", \
	               ["images/puzzlebox.ico", \
	                "images/1-upper_left-orange.png", \
	                "images/1-upper_left-white.png", \
	                "images/2-up-orange.png", \
	                "images/2-up-white.png", \
	                "images/3-upper_right-orange.png", \
	                "images/3-upper_right-white.png", \
	                "images/7-lower_left-orange.png", \
	                "images/7-lower_left-white.png", \
	                "images/8-down-orange.png", \
	                "images/8-down-white.png", \
	                "images/9-lower_right-orange.png", \
	                "images/9-lower_right-white.png", \
	                "images/puzzlebox_logo.png", \
	                "images/brainstorms-aileron_left.svg", \
	                "images/brainstorms-aileron_right.svg", \
	                "images/brainstorms-elevator_forward.svg", \
	                "images/brainstorms-elevator_reverse.svg", \
	                "images/brainstorms-fly_forward.svg", \
	                "images/brainstorms-hover.svg", \
	                "images/brainstorms-land_arrow.svg", \
	                "images/brainstorms-rudder-left.svg", \
	                "images/brainstorms-rudder-right.svg", \
	                "images/brainstorms_stop.svg", \
	                "images/brainstorms_wheelchair_forward.svg", \
	                "images/brainstorms_wheelchair_left.svg", \
	                "images/brainstorms_wheelchair_reverse.svg", \
	                "images/brainstorms_wheelchair_right.svg", \
	                "images/braintorms-throttle_up.svg", \
	                "images/puzzlebox_helicopter.svg", \
	               ]),
	]
	
	# Add the mpl mpl-data folder and rc file
#	data_files += matplotlib.get_py2exe_datafiles()
	
#	matplotlib.use('Qt4Agg') # overrule configuration


else:
	options={}
	
	data_files=[("/etc/puzzlebox_brainstorms", \
	               ["puzzlebox_brainstorms_configuration.ini"]),
	            ("/usr/share/puzzlebox_brainstorms/images", \
	               ["images/puzzlebox.ico", \
	                "images/1-upper_left-orange.png", \
	                "images/1-upper_left-white.png", \
	                "images/2-up-orange.png", \
	                "images/2-up-white.png", \
	                "images/3-upper_right-orange.png", \
	                "images/3-upper_right-white.png", \
	                "images/7-lower_left-orange.png", \
	                "images/7-lower_left-white.png", \
	                "images/8-down-orange.png", \
	                "images/8-down-white.png", \
	                "images/9-lower_right-orange.png", \
	                "images/9-lower_right-white.png", \
	                "images/puzzlebox_logo.png", \
	                "images/brainstorms-aileron_left.svg", \
	                "images/brainstorms-aileron_right.svg", \
	                "images/brainstorms-elevator_forward.svg", \
	                "images/brainstorms-elevator_reverse.svg", \
	                "images/brainstorms-fly_forward.svg", \
	                "images/brainstorms-hover.svg", \
	                "images/brainstorms-land_arrow.svg", \
	                "images/brainstorms-rudder-left.svg", \
	                "images/brainstorms-rudder-right.svg", \
	                "images/brainstorms_stop.svg", \
	                "images/brainstorms_wheelchair_forward.svg", \
	                "images/brainstorms_wheelchair_left.svg", \
	                "images/brainstorms_wheelchair_reverse.svg", \
	                "images/brainstorms_wheelchair_right.svg", \
	                "images/braintorms-throttle_up.svg", \
	                "images/puzzlebox_helicopter.svg", \
	               ]),
	            ("/usr/share/applications", \
	               ["puzzlebox_brainstorms.desktop"]),
	           ]



setup(
	name='puzzlebox_brainstorms',
	version='0.8.4',
	description='Puzzlebox Brainstorms provides Brain-Computer Interface (BCI) controls for robots and devices',
	author='Steve Castellotti',
	author_email='sc@puzzlebox.info',
	url='http://brainstorms.puzzlebox.info',
	py_modules=['Puzzlebox', \
	            'Puzzlebox.Brainstorms', \
	            'Puzzlebox.Brainstorms.Server', \
	            'Puzzlebox.Brainstorms.Client', \
	            'Puzzlebox.Brainstorms.Interface', \
	            'Puzzlebox.Brainstorms.Interface_Design', \
	            'Puzzlebox.Brainstorms.Helicopter_Control', \
	            'Puzzlebox.Brainstorms.iRobot_Control', \
	            'Puzzlebox.Brainstorms.NXT_Control', \
	            'Puzzlebox.Brainstorms.RC_Car_Control', \
	            'Puzzlebox.Brainstorms.Wheelchair_Control', \
	            'Puzzlebox.Brainstorms.Configuration', \
	            'Puzzlebox.Brainstorms.iRobot.pyrobot', \
	            'Puzzlebox.Brainstorms.ThinkGear.Client', \
	            'brainstorms-local', \
	            'brainstorms-network', \
	           ], \
#	console=["puzzlebox_brainstorms_remote_control.py", \
#	         "puzzlebox_brainstorms_network_server.py", \
#	         "puzzlebox_brainstorms_network_client.py", \
#	         "puzzlebox_brainstorms_network_client_thinkgear.py"],
	console=["brainstorms-local.py", \
	         "brainstorms-network.py"
	],
#	options={"py2exe":{"includes":["sip"]}},
	options=options, \
	zipfile = r'lib\library.zip',
#	data_files=[("puzzlebox_brainstorms_configuration.ini"),
#		("images",
#		 glob.glob(os.path.join('images', '*.*'))),
#		 #("fonts",
#		 #glob.glob(os.path.join('fonts', '*.*')))
#	],
	data_files=data_files, \
	windows=[ \
		#{
		 #"script": "puzzlebox_brainstorms_network_server.py",
		 #"icon_resources": [(1, \
		 #os.path.join("images", "puzzlebox.ico"))]
		#},
		{
		 "script": "brainstorms-local.py",
		 "icon_resources": [(1, \
		 os.path.join("images", "puzzlebox.ico"))]
		},
#		{
#		 "script": "puzzlebox_brainstorms_client_interface_local.py",
#		 "icon_resources": [(1, \
#		 os.path.join("images", "puzzlebox.ico"))]
#		},
	],
	classifiers=[ \
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: End Users/Desktop',
		'Programming Language :: Python',
		'Operating System :: OS Independent',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Topic :: Scientific/Engineering :: Human Machine Interfaces',
	],
)

