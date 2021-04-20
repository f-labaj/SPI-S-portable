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

from . import types_builder
from . import types

from collections import namedtuple
from string import ascii_letters, digits

# -----------------------------------------------------------------------------
# constants

VARIABLE_SIZE = "variable size"

BYTE_ORDER_NATIVE = '='
BYTE_ORDER_LITTLE_ENDIAN = '<'
BYTE_ORDER_BIG_ENDIAN = '>'
BYTE_ORDER_NETWORK = '!'

BYTE_ORDER_LIST = [BYTE_ORDER_NATIVE, BYTE_ORDER_LITTLE_ENDIAN, BYTE_ORDER_BIG_ENDIAN, BYTE_ORDER_NETWORK]

# -----------------------------------------------------------------------------
# exceptions

class EndOfFileError( EOFError ):
    pass
    
class ParsingError( Exception ):
    pass

class WriteError( Exception ):
    pass

# -----------------------------------------------------------------------------
# parsing and validation of definition
        
def _parse_dsl_definition( objectDef ):
    triplets = types_builder._parse_tuples( objectDef )
    items = []
    for row in triplets:
        if len(row) != 3:
            raise ParsingError( 'too many tokens in definition "%s"' % str(row) )
            
        typeObj = types.__dict__.get( 't_'+row[1].replace('@','_'), None )
        if not typeObj:
            raise ParsingError( 'unknown type "%s"' % row[1] )
        
        items.append( (row[0], typeObj, row[2]) )
    return items

def _validate_identifier( ident, names=set() ):
    if ident[0] not in ascii_letters:
        raise ParsingError( 'invalid identifier "%s"' % ident )
    for c in ident:
        if c not in ascii_letters and c not in digits and c != '_':
            raise ParsingError( 'invalid identifier "%s"' % ident )
    if ident in names:
        raise ParsingError( 'duplicated identifier "%s"' % ident )

def _validate_count_expression( expr, validNames ):
    def is_int( x ):
        try:
            n = int(x)
            return True
        except ValueError:
            return False
    def is_identifier( x ):
        try:
            _validate_identifier( x )
            return True
        except ParsingError:
            return False
    
    if is_int( expr ):
        n = int(expr)
        if n < 0:
            raise ParsingError( 'count expression "%s" resolves to negative integer' % expr )
        return n

    validChars = '()+-*/% \t'
    varnames = expr
    for c in validChars:
        varnames = varnames.replace( c, ':' )
    varnames = [v for v in varnames.split(':') if is_identifier(v) and v not in validNames]
    if varnames:
        raise ParsingError( 'invalid identifier in count expression "%s" (non scalar integer type or unknown identifier)' % expr )
    
    for c in expr:
        if c not in validChars and c not in ascii_letters and c not in digits and c != '_':
            raise ParsingError( 'invalid chars in count expression "%s"' % expr )
    
    return expr

_Item = namedtuple( "Item", "n,t,name".split(',') )

def _validate_definition( itemList ):
    byteCount = 0
    names = set([])
    inames = set([])
    validatedItems = []
    for item in itemList:
        if len(item) != 3:
            raise ParsingError( 'too many tokens in definition "%s"' % str(item) )
        countExpression, typeObj, itemName = item
        if type(typeObj) != types_builder.Type:
            raise ParsingError( 'type supplied not a class Type object "%s"' % str(item) )
        countExpression = _validate_count_expression( countExpression, inames )
        _validate_identifier( itemName, names )
        names.add( itemName )
        if typeObj.isInteger and countExpression == 1:
            inames.add( itemName )

        validatedItems.append( _Item( countExpression, typeObj, itemName ) )
        if type(byteCount) == int and type(countExpression) == int:
            byteCount += typeObj.singleItemSize*countExpression
        else:
            byteCount = VARIABLE_SIZE
    return validatedItems, byteCount

# -----------------------------------------------------------------------------
# global read/write functions

def _fread( f, n ):
    buff = f.read( n )
    if len(buff) != n:
        raise EndOfFileError
    return buff
    
def _fwrite( f, x ):
    f.write( x )

# -----------------------------------------------------------------------------
# BinIO

class Struct( object ):
    def __init__( self, model ):
        self.__model = model
    def get_size_in_bytes( self ):
        return self.__model.get_size_in_bytes( self.__dict__ )
    def clear( self ):
        self.__model.clear( self.__dict__ )

class BinIO( object ):
    def __init__( self, items, byteCount ):
        self.__items = items
        self.__byteSize = byteCount
        self.clear()
        
    def get_size_in_bytes( self, obj=None ):
        """ returns byte count of this struct or VARIABLE_SIZE """
        if self.__byteSize == VARIABLE_SIZE:
            this = obj if obj else self.__dict__
            bcount = 0
            for item in self.__items:
                n = BinIO._get_actual_count( item, this )
                bcount += n*item.t.singleItemSize
        else:
            bcount = self.__byteSize
        return bcount
        
    def clear( self, obj=None ):
        """ initializes all items to default value """
        this = obj if obj else self.__dict__
        for item in self.__items:
            n = BinIO._get_actual_count( item, this )
            v = item.t.get_default_value( n )
            this[item.name] = v
            
    def read_struct( self, f, byteOrder=BYTE_ORDER_NATIVE ):
        x = Struct( self )
        self._read( f, byteOrder, x.__dict__ )
        return x

    def read_dict( self, f, byteOrder=BYTE_ORDER_NATIVE ):
        x = dict()
        self._read( f, byteOrder, x )
        return x

    def read( self, f, byteOrder=BYTE_ORDER_NATIVE ):
        """ read data from f with given byteOrder
            returns number of bytes read
        """
        self._read( f, byteOrder, self.__dict__ )
                
    def write_struct( self, f, x, byteOrder=BYTE_ORDER_NATIVE ):
        """ write data from struct x to file f with given byte order
            no data is written until all values have been correctly packaged
            returns number of bytes written
        """
        return self._write( f, byteOrder, x.__dict__ )

    def write_dict( self, f, x, byteOrder=BYTE_ORDER_NATIVE ):
        """ write data from dict x to file f with given byte order
            no data is written until all values have been correctly packaged
            returns number of bytes written
        """
        return self._write( f, byteOrder, x )

    def write( self, f, byteOrder=BYTE_ORDER_NATIVE ):
        """ write data to file f with given byte order
            no data is written until all values have been correctly packaged
            returns number of bytes written
        """
        return self._write( f, byteOrder, self.__dict__ )

    def _read( self, f, byteOrder, dst ):
        assert byteOrder in BYTE_ORDER_LIST
        self.clear( dst )
        bytesRead = 0
        for item in self.__items:
            n = BinIO._get_actual_count( item, dst )
            bcount = item.t.get_byte_count( n )
            values = item.t.read( n, byteOrder, _fread( f, bcount ) )
            bytesRead += bcount
            dst[item.name] = self._process_read( values, item.t, n )
        return bytesRead

    def _write( self, f, byteOrder, src ):
        """ write data to f with given byteOrder
            no data is written until all values have been correctly packaged
            returns number of bytes written
        """
        assert byteOrder in BYTE_ORDER_LIST
        toWrite = b''
        for item in self.__items:
            n = BinIO._get_actual_count( item, src )
            values = self._process_write( src[item.name], item.t, n )
            if values:
                try:
                    p = item.t.write( n, byteOrder, values )
                except struct.error:
                    raise WriteError( 'error packing item "%s" (value "%s") into bytes (wrong type, value out of range, etc)' % (item.name, src[item.name]) )
                toWrite += p

        _fwrite( f, toWrite )
        return len(toWrite)

    @staticmethod
    def _get_actual_count( item, obj ):
        if type(item.n) == int:
            n = item.n
        else:
            n = eval( item.n, dict(), obj )
        return n


    def _process_read( self, values, typeObject, n ):
        tc = typeObject.name
        if tc == 'byte':
            values = values[0]
        elif tc in ['string','char']:
            values = values[0]
            if not typeObject.codec:
                values = values.decode( 'ascii' ).rstrip('\x00')
            else:
                values = values.decode( typeObject.codec ).rstrip('\x00')
        elif n == 1:
            values = values[0]
        else:
            values = [x for x in values]
        return values

    def _process_write( self, values, typeObject, n ):
        tc = typeObject.name
        if tc == 'byte':
            values = values[:n]
            if len(values) < n:
                values += b'\x00'*(n-len(values))
            values = [values]
        elif tc in ['string','char']:
            if not typeObject.codec:
                values = values.encode( 'ascii' )
            else:
                tmp = values.encode( typeObject.codec )
                if typeObject.codec == 'utf16':
                    if tmp[:2] == b'\xff\xfe' and tmp[2:].decode( typeObject.codec ) == values:
                        tmp = tmp[2:]                    
                values = tmp
            if len(values) < n:
                values += b'\x00'*(n-len(values))
            values = [values]
        elif n == 1:
            values = [values]
        else:
            values = values[:n]
            if len(values) < n:
                values.extend( [typeObject.defValue]*(n-len(values)) )
        
        return [x for x in values]

def new( objectDef ):
    if type(objectDef) == str:
        objectDef = _parse_dsl_definition( objectDef )
    
    itemList, byteCount = _validate_definition( objectDef )
    return BinIO( itemList, byteCount )

