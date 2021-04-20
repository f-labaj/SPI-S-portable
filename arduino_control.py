import serial
import time, sys

ser = serial.Serial(
					port='COM3',
					baudrate=9600,
					parity=serial.PARITY_NONE,
					stopbits=serial.STOPBITS_ONE,
					bytesize=serial.EIGHTBITS,
					timeout=0)

print("connected to: " + ser.portstr)

ser.flush()

while True:
	ser.write(b't')
	time.sleep(0.5)
	b1 = int.from_bytes(ser.read(1), 'little')
	time.sleep(0.1)
	b2 = int.from_bytes(ser.read(1), 'little')
	x = b1 + b2*256
	print(x)
	time.sleep(0.2)

ser.close()