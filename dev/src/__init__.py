import os, sys
# Makes relative imports to work in Python 3.6
# without the need of '.' before the name of the
# package or py file.
# Allows for consistent syntax of relative imports
# across python2 and python3.
version = '2.0.0-beta'
sys.path.append(os.path.dirname(os.path.realpath(__file__)))