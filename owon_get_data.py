# From: https://stackoverflow.com/questions/59105167/pyusb-reading-from-a-usb-device
# Modified to return dev from connect() and add it to subsequent commands

# Alternatives:
#   - https://github.com/robert-hh/owonread
#   - https://www.rei-labs.net/fetching-data-from-owon-sds7102v-to-pc/

### read data from a Peaktech 1337 Oscilloscope (OWON)
import usb.core
import usb.util

def connect():
    dev = usb.core.find(idVendor=0x5345, idProduct=0x1234)

    if dev is None:
        raise ValueError('Oscilloscope device not found!')
    else:
        print(dev)
        dev.set_configuration()
        return dev
    
def send(dev, cmd):
    # address taken from results of print(dev):   ENDPOINT 0x3: Bulk OUT
    dev.write(3,cmd)
    # address taken from results of print(dev):   ENDPOINT 0x81: Bulk IN
    result = (dev.read(0x81,100000,1000))
    return result

def get_id(dev):
    return send(dev, '*IDN?').tobytes().decode('utf-8')

def get_data(dev, ch):
	# TODO - change to peak measurement
	
	
    # first 4 bytes indicate the number of data bytes following
    rawdata = send(dev, ':DATA:WAVE:SCREen:CH{}?'.format(ch))
    data = []
    for idx in range(4,len(rawdata),2):
        # take 2 bytes and convert them to signed integer using "little-endian"
        point = int().from_bytes([rawdata[idx], rawdata[idx+1]],'little',signed=True)
        data.append(point/4096)  # data as 12 bit
    return data

def get_header(dev):
    # first 4 bytes indicate the number of data bytes following
    header = send(dev, ':DATA:WAVE:SCREen:HEAD?')
    header = header[4:].tobytes().decode('utf-8')
    return header

def save_data(ffname,data):
    f = open(ffname,'w')
    f.write('\n'.join(map(str, data)))
    f.close()

# print(get_id())
# header = get_header()
# data = get_data(1)
# save_data('Osci.dat',data)


# alternative
# https://github.com/robert-hh/owonread

#

# https://stackoverflow.com/questions/59105167/pyusb-reading-from-a-usb-device

#

# alternative below from https://www.rei-labs.net/fetching-data-from-owon-sds7102v-to-pc/

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# print "Open socket"
# # set IP and socket to your oscilloscope
# s.connect(('192.168.88.10',3000))
# print "Send command"
 
# s.setblocking(0)
 
# #s.send('STARTBIN')
# #s.send('STARTBMP')
# s.send('STARTMEMDEPTH')
 
# chunk_size = 1024 * 16
# rcvd_data = 0
# full_data = ''
# timeout = 0
 
# print "Read data ",
    
# while (timeout<60):
    # if(rcvd_data == 0):
        # timeout = timeout + 1
    # else:
        # timeout = 0
    # try:
        # data_chunk = s.recv(chunk_size)
        # rcvd_data = len(data_chunk)
        # full_data += data_chunk
        # print rcvd_data,",",
    # except socket.error, e:
        # if e.args[0] == errno.EWOULDBLOCK: 
            # rcvd_data = 0
        # else:
            # print e
            # break
    # time.sleep(0.1)
 
 
# print "Close socket"
# s.close()
 
# print len(full_data)
 
# print "Write file"
# with open("Output.bin", "wb") as text_file:
    # text_file.write(full_data)
