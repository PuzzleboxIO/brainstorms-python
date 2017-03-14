brainstorms-python
==================


Puzzlebox Brainstorms


Copyright (2010-2017)

by Puzzlebox Productions, LLC

https://puzzlebox.io/brainstorms


License: GNU Affero General Public License v3.0
https://www.gnu.org/licenses/agpl-3.0.html


============

Download Releases:

Github: https://github.com/PuzzleboxIO/brainstorms-python/tree/master/releases


============

Required Python Modules:
- pyside
- simplejson
- serial
- jaraco.nxt

============

Instructions:

- Requires downloading and configuration of Puzzlebox Synapse:

https://github.com/PuzzleboxIO/synapse-python

- Create a symlink inside root directory to Synapse:

Example: ln -s ../synapse-python/Puzzlebox/Synapse Synapse


============

Examples:

macOS (via MacPorts):

$ sudo port install py27-pyside py27-simplejson py27-serial py27-matplotlib

$ sudo easy_install-2.7 jaraco.nxt

$ git clone https://github.com/PuzzleboxIO/synapse-python

$ git clone https://github.com/PuzzleboxIO/brainstorms-python

$ cd brainstorms-python/Puzzlebox

$ ln -s ../synapse-python/Puzzlebox/Synapse Synapse

$ cd ..

$ python2.7 brainstorms-local.py
