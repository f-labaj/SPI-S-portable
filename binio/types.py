# -*- coding: utf8 -*-
""" python module binio
Module that implements a simple class for reading and writing structured binary data

Version: 1.2.3b
Author:  Alejandro López Correa
Contact: alc@spika.net
URL:     http://spika.net/py/binio/
License: MIT License

Tested with python 2.7 and 3.2

(c) Alejandro López Correa, 2013
"""
# this module will normally be imported with an 'from binio.types import *'
# this code avoids namespace pollution and also solves a python 3 collision with standard module types

import sys
from . import types_builder
for k in dir(types_builder):
    if k.startswith( 't_' ):
        setattr( sys.modules[__name__], k, getattr( types_builder, k ) )
        
del k
del sys    
del types_builder
