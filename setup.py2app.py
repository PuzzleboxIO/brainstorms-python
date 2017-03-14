"""
This is a setup.py script generated by py2applet

Usage:
    python2.7 setup.py py2app
"""

from setuptools import setup

APP = ['brainstorms-local.py']

data_files=[ \
	(".", \
	#("Content/Resources", \
		["puzzlebox_brainstorms_configuration.ini"]),
	("images", \
		["images/puzzlebox.ico", \
			"images/puzzlebox.icns", \
			"images/puzzlebox_logo.png", \
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
		]), \
	#("qt_menu.nib", \
		#["/opt/local/lib/Resources/qt_menu.nib/classes.nib", \
			#"/opt/local/lib/Resources/qt_menu.nib/info.nib", \
			#"/opt/local/lib/Resources/qt_menu.nib/keyedobjects.nib", \
		#]), \
]

data_files=[]

OPTIONS = { \
	#'argv_emulation': True, \
	'argv_emulation': False, \
	'iconfile': 'images/puzzlebox.icns', \
	'strip': True, \
	
	# Semi-standalone is an option you can enable with py2app that makes 
	# your code reliant on the version of Python that is installed with the OS.
	# You also need to enable site-packages, as well (which apparently encourages
	# py2app to create the links to Python necessary for getting the bundle up
	# and running, although it's only supposed to tell it to include the
	# system and user site-packages in the system path)
	# http://beckism.com/2009/03/pyobjc_tips/
	
	#'semi_standalone': True, \
	#'site_packages': True, \
	
	'includes': [ \
		'PySide.QtSvg', \
	], \
	
	'excludes': ['PyQt4', 'sip'], \
	
	
	'frameworks': [ \
		"/opt/local/share/qt4/plugins/imageformats/libqjpeg.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqgif.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqico.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqmng.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqsvg.dylib", \
		"/opt/local/share/qt4/plugins/imageformats/libqtiff.dylib", \
	], \
	
	"resources": [ \
		"puzzlebox_brainstorms_configuration.ini", \
		#"images/puzzlebox.ico", \
		#"/opt/local/lib/Resources/qt_menu.nib/classes.nib", \
		#"/opt/local/lib/Resources/qt_menu.nib/info.nib", \
		#"/opt/local/lib/Resources/qt_menu.nib/keyedobjects.nib", \
	], \
}

setup(
	
	name='Puzzlebox Brainstorms',
	version='0.8.0',
	description='Puzzlebox Brainstorms provides Brain-Computer Interface (BCI) controls for robots and devices',
	author='Steve Castellotti',
	author_email='sc@puzzlebox.info',
	url='http://brainstorms.puzzlebox.info',
	
	classifiers=[ \
		'Development Status :: 5 - Production/Stable',
		'Intended Audience :: End Users/Desktop',
		'Programming Language :: Python',
		'Operating System :: OS Independent',
		'License :: Commercial',
		'Topic :: Scientific/Engineering :: Human Machine Interfaces',
	],
	
	app=APP,
	data_files=data_files,
	options={'py2app': OPTIONS},
	setup_requires=['py2app'],

)
