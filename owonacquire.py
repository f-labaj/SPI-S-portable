# -*- coding: utf8 -*-

""" python module owonbin
Module that captures data from OWON SDS7102 oscilloscope through LAN interface

Version: 20131109.1
Author:  Alejandro López Correa
Contact: alc@spika.net
URL:     http://spika.net/py/owontool/
License: MIT License http://opensource.org/licenses/MIT

Tested with python 2.7 and 3.3

(c) Alejandro López Correa, 2013
"""

import socket

class ErrorConnect( Exception ):
    def __init__( self, message ):
        Exception.__init__( self )
        self.message = message

class Oscilloscope( object ):
    def __init__( self, ip, port ):
        self.skt = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.skt.settimeout( 3 )
        try:
            self.skt.connect( (ip, port) )
        except socket.timeout:
            raise ErrorConnect( 'timeout' )
        except socket.error as e:
            raise ErrorConnect( e.strerror )
        
    def close( self ):
        self.skt.close()
    
    @staticmethod
    def parse_header( header ):
        if type(header[0]) != int:
            header = map( ord, header )
        fileLen = (header[3]<<24) + (header[2]<<16) + (header[1]<<8) + header[0]
        flag = header[8]
        return fileLen, flag

    def get_screenshot( self ):
        skt = self.skt

        skt.sendall( b"STARTBMP" )

        data = skt.recv( 4096 )
        fileLen, flag = self.parse_header( data[:12] )
        data = data[12:]
        while len(data) < fileLen:
            block = skt.recv( 4096 )
            data += block
            
        return data

    def get_vector_data( self ):
        skt = self.skt

        skt.sendall( b"STARTBIN" )

        data = skt.recv( 4096 )
        fileLen, flag = self.parse_header( data[:12] )

        channel = flag-128
        data = data[12:]
        while len(data) < fileLen:
            block = skt.recv( 4096 )
            data += block
           
        return data

    def get_deep_vector_data( self ):
        skt = self.skt

        skt.sendall( b"STARTMEMDEPTH" )

        data = skt.recv( 4096 )
        fileLen, flag = self.parse_header( data[:12] )

        channel = flag-128
        data = data[12:]
        while len(data) < fileLen:
            block = skt.recv( 4096 )
            data += block
           
        return data
