#!/bin/bash

#pyuic4 --output=qt4_form.py --indent=0 qt4_form.ui
#pyuic4 --output=../puzzlebox_brainstorms_client_interface_design.py --indent=0 qt4_form.ui
#pyuic4 --output=Puzzlebox/Brainstorms/Interface_Design.py --indent=0 interface/puzzlebox_brainstorms_interface_design.ui
pyside-uic --output=Puzzlebox/Brainstorms/Interface_Design.py --indent=0 interface/puzzlebox_brainstorms_interface_design.ui
