import serial
import time

# connect to Arduino
def init_serial(port_num, speed, tout):
    try:
        # DEBUG
        #print(port_num)
        #print(speed)
        #print(tout)
     
        ser = serial.Serial(
                        port=port_num,
                        baudrate=speed,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE,
                        bytesize=serial.EIGHTBITS,
                        timeout=tout)

        print("Connected to device on: " + ser.portstr)
        ser.flush()
        
        return ser
        
    except:
        print("Could not connect to Arduino! Check if it's plugged in / COM port number.")

# read value measured on Arduino, in two blocks
def get_value(ser, command):
    try:	
        ser.write(command)
        
        time.sleep(0.5)
        
        b1 = int.from_bytes(ser.read(1), 'little')
        
        time.sleep(0.1)
        
        b2 = int.from_bytes(ser.read(1), 'little')
        
        x = b1 + b2*256

        return x
    
    except:
        print("Error retrieving values from Arduino!")

# close the serial connection 
def close_serial(ser):
    if ser is not None:
        ser.close()