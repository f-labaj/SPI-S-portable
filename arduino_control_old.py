import serial
import time

## vars
# sampling
maxnsamp = 1200
values = []
maxval = 4096

## screen&trigger
w_scrn=900
h_scrn=600
x_scrn=20
y_scrn=20

x_ts=x_scrn+w_scrn+20
y_ts=y_scrn
w_ts=50
h_ts=20
trig_mode=0
trig_level=maxval/2
trig_offset=100
doread=False

## channels
x_ch=x_ts
y_ch=y_ts+4*h_ts
w_ch=w_ts
h_ch=h_ts
maxnchan=6
nchan=1
fchan=0
tchan=maxnchan
tmode=0
chanstat=[1,0,0,0,0,0]
nextchan=[0,0,0,0,0,0]

# bars
x_tb=x_ch
y_tb=y_ch+8*h_ch
w_tb=w_ch
h_tb=h_ch
tbms=[ 1, 2, 5, 10, 20, 50,100]
ADCPS=[16,32,64,128,128,128,128]
skipsamp=[ 1, 1, 1,  1,  2,  5, 10]
ntbval=len(tbms)
tbval=0

x_ns=x_tb
y_ns=y_tb+(ntbval+2)*h_tb
w_ns=w_tb
h_ns=h_tb
ns=[1200,600,300]
nns=len(ns)
ins=0
nsamp=ns[ins]

x_vb=x_ns
y_vb=y_ns+(nns+2)*h_ch
w_vb=w_ns
h_vb=h_ns
ivb=0
Vmax=[5.0,1.1]
Vdiv=[1.0,0.2]

## pulser
x_pb=x_scrn+50
y_pb=y_scrn+h_scrn+40
w_pb=w_scrn-50
h_pb=h_ch
pls_period  =[ 16, 40, 80,160,400,800,1600,4000,8000,16000,40000,10000,20000,50000,12500,25000,62500]
pls_prescale=[  1,  1,  1,  1,  1,  1,   1,   1,   1,    1,    1,    8,    8,    8,   64,   64,   64]
pls_len=[
	  [  1,  2,  3,   4,   5,   6,    7,   8,     9,   10,   11,   12,   13,   14,   15],
	  [  1,  2,  4,   6,   8,  12,   16,   20,   24,   28,   32,   34,   36,   38,   39],
	  [  1,  2,  4,   8,  16,  24,   32,   40,   48,   56,   64,   72,   76,   78,   79],
	  [  1,  2,  4,   8,  16,  32,   48,   80,  112,  128,  144,  152,  156,  158,  159],
	  [  1,  2,  4,   8,  20,  40,   80,  200,  320,  360,  380,  392,  396,  398,  399],
	  [  2,  4,  8,  16,  40,  80,  160,  400,  640,  720,  760,  784,  792,  796,  798],
	  [  4,  8, 16,  40,  80, 160,  320,  800, 1280, 1440, 1520, 1568, 1584, 1592, 1596],
	  [ 10, 20, 40,  80, 200, 400,  800, 2000, 3200, 3600, 3800, 3920, 3960, 3980, 3990],
	  [ 20, 40, 80, 160, 400, 800, 1600, 4000, 6400, 7200, 7600, 7840, 7920, 7960, 7980],
	  [ 40, 80,160, 400, 800,1600, 3200, 8000,12800,14400,15200,15680,15840,15920,15960],
	  [100,200,400, 800,2000,4000, 8000,20000,32000,36000,38000,39200,39600,39800,39900],
	  [ 25, 50,100, 200, 500,1000, 2000, 5000, 8000, 9000, 9500, 9800, 9900, 9950, 9975],
	  [ 50,100,200, 500,1000,2000, 5000,10000,16000,18000,19000,19600,19800,19900,19950],
	  [125,250,500,1000,2500,5000,10000,25000,40000,45000,48000,49000,49500,49750,49875],
	  [ 25, 50,125, 250, 500,1250, 2500, 6250,10000,11250,12000,12250,12375,12450,12475],
	  [ 50,100,250, 500,1000,2500, 5000,12500,20000,22500,24000,24500,24750,24900,24950],
	  [125,250,625,1250,2500,6250,12500,31250,50000,56250,60000,61250,61875,62250,62375]]
pls_np=len(pls_period)
pls_nl=len(pls_len[0])
pls_ip=8
pls_il=7


# serial comms
with serial.Serial('COM3', 115200, timeout=1) as dev:
	while True:
		try:
			dev.write(255)
			dev.write(bytes(str(nsamp / 0x100), encoding='utf8'))
			dev.write(bytes(str(nsamp % 0x100), encoding='utf8'))
			
			for i in range(maxnchan):
				dev.write(chanstat[i])
				
			for i in range(maxnchan):
				dev.write(nextchan[i])
				
			dev.write(fchan)
			dev.write(nchan)
			dev.write(tchan)
			dev.write(tmode)
			dev.write(ADCPS[tbval])
			dev.write(skipsamp[tbval])
			dev.write(ivb)
			dev.write(bytes(str(trig_level/16), encoding='utf8'))
			dev.write(bytes(str(trig_level/16), encoding='utf8'))
			dev.write(bytes(str(trig_offset/0x100), encoding='utf8'))
			dev.write(bytes(str(trig_offset%0x100), encoding='utf8'))
			if pls_prescale[pls_ip]== 1:
				dev.write(1);
			if pls_prescale[pls_ip]== 8:
				dev.write(2);
			if pls_prescale[pls_ip]==64:
				dev.write(3);
			dev.write(bytes(str(pls_period[pls_ip]/0x100), encoding='utf8'))
			dev.write(bytes(str(pls_period[pls_ip]%0x100), encoding='utf8'))
			dev.write(bytes(str(pls_len[pls_ip][pls_il]/0x100), encoding='utf8'))
			dev.write(bytes(str(pls_len[pls_ip][pls_il]%0x100), encoding='utf8'))
			
			sampletime=nsamp*(13*ADCPS[tbval]*skipsamp[tbval])/16e3
			sendtime=16.0*nsamp/115.2
			
			time.sleep(int((2.0*sampletime+1.1*sendtime) / 1000))
			
			while dev.in_waiting >= 2*nsamp+1:
				if dev.read() == 255:
					for isamp in range(nsamp):
						hsb=dev.read()
						lsb=dev.read()
						values.append(hsb*64+(lsb&0xFF))
						
						print(values)

					doread=False
					
		except KeyboardInterrupt:
			break