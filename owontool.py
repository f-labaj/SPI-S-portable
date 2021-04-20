#! /usr/bin/python
# -*- coding: utf8 -*-

""" owontool
Tool to capture data from OWON SDS7102 oscilloscope through LAN interface

Version: 20131109.1
Author:  Alejandro López Correa
Contact: alc@spika.net
URL:     http://spika.net/py/owontool/
License: MIT License http://opensource.org/licenses/MIT

Tested with python 2.7 and 3.3

(c) Alejandro López Correa, 2013
"""

from __future__ import print_function
import getopt, sys
import owonacquire, owonbin

RELEASE = "20131109.1"
OWON_TOOL_NAME = "Owon SDS7102 tool r" + RELEASE
DEFAULT_IP = "192.168.1.72"
DEFAULT_PORT = 3000
DEFAULT_OUTPUT_FILE = "data.txt"
DEFAULT_SCREENSHOT_FILE = "screenshot.bmp"

def usage():
    print( """\
{tool}
Usage: owontool.py [options]

-a ADDRESS         Oscilloscope's ip address. Defaults to
                   {ip}.
-p PORT            Oscilloscope's port. Defaults to {port}.
-d                 Selects deep data mode (all samples). If not 
                   specified, only on-screen data is captured.
-s                 Captures an screenshot (bmp format).
-o FILE            File path where data is stored. Defaults to
                   '{output}'
                   for sample data and to
                   '{screenshot}'
                   for screenshots.
-h                 Show this help.
-v                 Verbose mode.

--screenshot       Same as -s.  
--address=ADDRESS  Same as -a.
--port=PORT        Same as -p.
--deep             Same as -d.
--output=FILE      Same as -o.
--help             Same as -h.""".format( tool=OWON_TOOL_NAME, ip=DEFAULT_IP, port=DEFAULT_PORT, output=DEFAULT_OUTPUT_FILE, screenshot=DEFAULT_SCREENSHOT_FILE ) )

def main():
    addr = DEFAULT_IP
    port = DEFAULT_PORT
    output = None
    deep = False
    screenshot = False
    verbose = False

    try:
        opts, args = getopt.getopt( sys.argv[1:], "a:p:o:dshv", ["address=", "port=", "deep", "output=", "screenshot", "help"] )
    except getopt.GetoptError as err:
        print( err )
        usage()
        sys.exit( 2 )
        
    output = None
    verbose = False
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-s", "--screenshot"):
            screenshot = True
            if deep:
                print( "ERROR: deep sample capture already specified" )
                sys.exit( -2 )
        elif o in ("-a", "--address"):
            addr = a
        elif o in ("-p", "--port"):
            try:
                port = int(a)
                if port <= 0 or port > 65535:
                    raise ValueError
            except ValueError:
                print( "ERROR: port must be an integer in range [1,65535]" )
                sys.exit( -2 )
        elif o in ("-o", "--output"):
            output = a
        elif o in ("-d", "--deep"):
            deep = True
            if screenshot:
                print( "ERROR: screenshot capture already specified" )
                sys.exit( -2 )
        elif o in ("-h", "--help"):
            usage()
            sys.exit( 2 )
        else:
            print( "unhandled option %s" % o )
            sys.exit( -1 )

    if verbose:
        print( OWON_TOOL_NAME )
        print( "connecting to oscilloscope at %s:%i" % (addr,port) )
        
    try:
        scope = owonacquire.Oscilloscope( addr, port )
    except owonacquire.ErrorConnect as e:
        print( "connection error: %s" % e.message )
        sys.exit( -3 )
        
    if screenshot:
        if verbose:
            print( "capturing screenshot" )
        data = scope.get_screenshot()
        if output == None:
            output = DEFAULT_SCREENSHOT_FILE
        if verbose:
            print( "storing data to '%s'" % output )
        try:
            open( output, 'wb' ).write( data )
        except IOError as e:
            print( "error storing data: %s" % e.strerror )
    else:
        if output == None:
            output = DEFAULT_OUTPUT_FILE
        if deep:
            if verbose:
                print( "capturing deep vector data" )
            data = scope.get_deep_vector_data()
        else:
            data = scope.get_vector_data()
        if verbose:
            print( "data info:" )
            owonbin.show_data( data )
        if verbose:
            print( "storing data to '%s'" % output )
        try:
            output = open( output, 'wt' )
            owonbin.write_data_text_format( data, output )
        except IOError as e:
            print( "error storing data: %s" % e.strerror )
        
    scope.close()

if __name__ == "__main__":
    main()
