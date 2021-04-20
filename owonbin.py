# -*- coding: utf8 -*-

""" python module owonbin
Module that extracts data from OWON SDS7102 oscilloscope binary format

Version: 20131109.1
Author:  Alejandro López Correa
Contact: alc@spika.net
URL:     http://spika.net/py/owontool/
License: MIT License http://opensource.org/licenses/MIT

Tested with python 2.7 and 3.3

(c) Alejandro López Correa, 2013
"""

from __future__ import print_function

try:
    from io import BytesIO
except ImportError:
    from StringIO import StringIO as BytesIO

import struct
from collections import namedtuple
import binio

fileHeader = binio.new( """
            8 : string          : tag
            2 : uint8           : unknown1
           21 : string          : productId
           10 : uint8           : unknown2
            6 : uint8           : unknown3
            2 : uint8           : unknown4
            4 : uint8           : unknown5
            1 : uint8           : unknown6
""" )
channelHeader = binio.new( """
            3 : char            : channelName
            1 : int32           : blockLength
            1 : int32           : sampleFormat
            1 : int32           : unknown1
            1 : int32           : unknown2
            1 : int32           : sampleCount
            1 : int32           : unknown3
            1 : int32           : timeBaseCode
            1 : int32           : unknown4
            1 : int32           : vertSensCode
            5 : int32           : unknown5_10
""" )

vertSensTable = {   0x00 : 20,
                    0x01 : 50,
                    0x02 : 100,
                    0x03 : 200,
                    0x04 : 500,
                    0x05 : 1000,
                    0x06 : 2000,
                    0x07 : 5000,
                    0x08 : 10000,
                    0x09 : 20000,
                    0x0a : 50000,
                    0x0b : 100000
 }   # 100 seconds
timeBaseTable = {   0x00 : 2,
                    0x01 : 5,
                    0x02 : 10,
                    0x03 : 20,
                    0x04 : 50,
                    0x05 : 100,
                    0x06 : 200,
                    0x07 : 500,
                    0x08 : 1000,           # 1 microsecond
                    0x09 : 2000,
                    0x0a : 5000,
                    0x0b : 10000,
                    0x0c : 20000,
                    0x0d : 50000,
                    0x0e : 100000,
                    0x0f : 200000,
                    0x10 : 500000,
                    0x11 : 1000000,         # 1 millisecond
                    0x12 : 2000000,
                    0x13 : 5000000,
                    0x14 : 10000000,        # 10 ms
                    0x15 : 20000000,
                    0x16 : 50000000,
                    0x17 : 100000000,
                    0x18 : 200000000,
                    0x19 : 500000000,
                    0x1a : 1000000000,      # 1 second
                    0x1b : 2000000000,
                    0x1c : 5000000000,
                    0x1d : 10000000000,
                    0x1e : 20000000000,
                    0x1f : 50000000000,
                    0x20 : 100000000000 }   # 100 seconds

def parse_channel_header( data ):
    hdr = channelHeader.read_struct( BytesIO( data ) )

#    print hdr.channelName
#    print hdr.blockLength
#    print hdr.sampleFormat
#    print hdr.unknown1
#    print hdr.unknown2
#    print hdr.sampleCount
#    print hdr.unknown3
#    print hdr.timeBaseCode
#    print hdr.unknown4
#    print hdr.vertSensCode
#    print hdr.unknown5_10

    timeBase = (timeBaseTable[hdr.timeBaseCode]/float(1000000)) # ms
    vertSens = (vertSensTable[hdr.vertSensCode]/float(1000))    # volts
    return hdr.channelName, hdr.sampleFormat, hdr.sampleCount, timeBase, vertSens

ChannelData = namedtuple( 'ChannelData', 'channel, samples, timeBaseMS, vertSensV' )

def parse_channel( data ):
    channelHeaderSize = channelHeader.get_size_in_bytes()

    channelName, sampleFormat, sampleCount, timeBase, vertSens = parse_channel_header( data[:channelHeaderSize] )

    data = data[channelHeaderSize:]
    assert sampleFormat in [2,3]
    
    if sampleFormat == 2:
        sampleDepth = 2
        sampleT = 'h'
    elif sampleFormat == 3:
        sampleDepth = 1
        sampleT = 'b'

    samples = data[:sampleCount*sampleDepth]
    samples = struct.unpack( '<' + sampleT*sampleCount, data[:sampleCount*sampleDepth] )
    cdata = ChannelData( channelName, samples, timeBase, vertSens )
    data = data[sampleCount*sampleDepth:]
    
    return cdata, data
    

def parse_data( data ):
    fileHeaderSize = fileHeader.get_size_in_bytes()
    #fileHeaderData = fileHeader.read_struct( StringIO.StringIO( data[:fileHeaderSize] ) )
    fileHeaderData = fileHeader.read_struct( BytesIO( data[:fileHeaderSize] ) )
    tag = fileHeaderData.tag
    pid = fileHeaderData.productId.strip()
    data = data[fileHeaderSize:]

    cdata, data = parse_channel( data )
    channelDataList = [cdata]
    while len(data) > 0:
        cdata, data = parse_channel( data )
        channelDataList.append( cdata )
        
    return pid, channelDataList
        
def show_data( data ):
    pid, channelDataList = parse_data( data )    
    print( pid )
    for channelData in channelDataList:
        print( 'channel:', channelData.channel )
        print( 'samples:', len(channelData.samples) )
        print( 'timeBase:', channelData.timeBaseMS, 'ms' )
        print( 'vertSens:', channelData.vertSensV, 'v' )
        #samples = channelData.samples
        #print( 'sample stats: max %3i min %3i avg %6.2f' % (max(samples), min(samples), (float(sum(samples))/len(samples))) )

def write_data_text_format( data, f ):
    pid, channelDataList = parse_data( data )    
    
    f.write( 'productID: %s\n' % pid )
    
    for channelData in channelDataList:
        f.write( '%s\n' % ('-'*20) )
        f.write( 'channel: %s\n' % channelData.channel )
        f.write( 'time base: %s ms\n' % channelData.timeBaseMS )
        f.write( 'vert sens: %s v\n' % channelData.vertSensV )
        f.write( 'sample count: %i\n' % len(channelData.samples) )
        f.write( 'sample data: milliseconds, volts, raw sample value [-128,127]\n' )
        for i,sample in enumerate(channelData.samples):
            t = i * channelData.timeBaseMS
            v = sample*channelData.vertSensV*5/127.0
            f.write( '%.6f,%f,%i\n' % (t,v,sample) )

