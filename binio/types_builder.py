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

This file contains types
"""

import struct

# astr and ustr are needed because of differences between python 2 and 3 regarding strings and byte buffers
# astr: constructor for "ascii string"
astr = lambda : str()
# ustr: constructor for "unicode string"
try:
    unicode()
    ustr = lambda : unicode()
except:
    ustr = lambda : str()        # python 3

__TYPES = """\
byte            : s : b''
int8            : b : 0
i8              : b : 0
uint8           : B : 0
u8              : B : 0
short           : h : 0
int16           : h : 0
i16             : h : 0
ushort          : H : 0
uint16          : H : 0
u16             : H : 0
int             : i : 0
int32           : i : 0
i32             : i : 0
uint            : I : 0
uint32          : I : 0
u32             : I : 0
int64           : q : 0
i64             : q : 0
uint64          : Q : 0
u64             : Q : 0
float           : f : 0.0
float32         : f : 0.0
float64         : d : 0.0
double          : d : 0.0
char            : s : astr()
string          : s : astr()
string@utf8     : s : ustr()
string@utf16    : s : ustr()"""

def _parse_tuples( txt ):
    rows = []
    for line in txt.split( "\n" ):
        line = line.strip()
        line = line.split( '#' )[0]
        if line:
            tokens = [t.strip() for t in line.split(':')]
            rows.append( tokens )
    return rows

class Type( object ):
    def __init__( self, name, stype, defValue, codec=None ):
        self.name = name
        self.stype = stype
        self.defValue = defValue
        self.codec = codec
        self.singleItemSize = struct.calcsize( '='+self.stype )
    @property
    def fullName( self ):
        nm = self.name
        if self.codec:
            nm += '_'+self.codec
        return nm
    @property
    def isInteger( self ):
        return self.stype in 'bBhHiIqQ'

    def get_format( self, n, byteOrder ):
        return '%s%i%s' % ( byteOrder, n, self.stype )
        
    def get_byte_count( self, n ):
        return n*self.singleItemSize

    def read( self, n, byteOrder, data ):
        values = struct.unpack( self.get_format( n, byteOrder ), data )
        return values

    def write( self, n, byteOrder, values ):
        return struct.pack( self.get_format( n, byteOrder ), *values )
        
    def get_default_value( self, n ):
        if n == 1:
            return self.defValue
        elif self.name in ['char','string','byte']:
            return self.defValue*n
        else:
            return [self.defValue]*n

def _generate_types( types ):
    rows = _parse_tuples( types )
    for row in rows:
        assert len(row) == 3
        x = row[0].split('@')
        t = Type( x[0], row[1], eval(row[2]), None if len(x)==1 else x[1] )
        globals()['t_'+t.fullName] = t

_generate_types( __TYPES )
