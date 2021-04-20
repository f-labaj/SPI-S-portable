import serial
import time

def init_serial():
	try:
		# TODO - add GUI-side user declaration of COM port number
		ser = serial.Serial(
						port='COM3',
						baudrate=9600,
						parity=serial.PARITY_NONE,
						stopbits=serial.STOPBITS_ONE,
						bytesize=serial.EIGHTBITS,
						timeout=0)

		print("Connected to: " + ser.portstr)
		ser.flush()
		
		return ser
		
	except:
		print("Could not connect to Arduino! Check if it's plugged in / COM port number.")

def get_value(ser):
	try:	
		ser.write(b't')
		
		time.sleep(0.5)
		
		b1 = int.from_bytes(ser.read(1), 'little')
		
		time.sleep(0.1)
		
		b2 = int.from_bytes(ser.read(1), 'little')
		
		x = b1 + b2*256

		return x
	
	except:
		print("Error retrieving values from Arduino!")
	
def close_serial(ser):
	if ser is not None:
		ser.close()