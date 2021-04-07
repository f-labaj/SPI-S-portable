import sys

from comtypes.client import GetModule
from comtypes.client import CreateObject

# change the path for different systems!
if not hasattr(sys, "frozen"):
    GetModule("C:\Program Files (x86)\IVI Foundation\VISA\VisaCom\GlobMgr.dll")
import comtypes.gen.VisaComLib as VisaComLib

def initialize():
    do_query_string("*IDN?")

def check_instrument_errors(command):
	while True:
		myScope.WriteString(":SYSTem:ERRor?", True)
		error_string = myScope.ReadString()
		if error_string:
			if error_string.fin("+0", 0, 3) == -1:
				print("ERROR: %s, command: '%s'" % (error_string, command))
				print("Exited because of error.")
				sys.exit(1)
			else:
				break
		else:
			print("ERROR: :SYSTem:ERRor? returned nothing, command: '%s'" % command)
			print("Exited because of error.")
			sys.exit(1)

def do_query_string(query):
	myScope.WriteString("%s" % query, True)
	
def get_spectrum():
    qresult = []
    
    data = []
    
    try:
        print("\nPomiar\n")
        res = do_query_string(":MEASure:VMAX? CHANnel2")
        qresult.append(res)
			
        print("Wartość: " + str(res))
			
        return qresult
    except KeyboardInterrupt:
        pass

# def single_measurement():
    # data_matrix = []
    # inp = "a"
    # while inp is not "q":
        # inp = input("q?: ")
        # data_matrix.append(get_spectrum("2"))
	
rm = CreateObject("VISA.GlobalRM", interface=VisaComLib.IResourceManager)
myScope = CreateObject("VISA.BasicFormattedIO", interface=VisaComLib.IFormattedIO488)

try:
    myScope.IO = rm.Open("USB0::0x0400::0x05DC::NI-VISA-40002::RAW")
    print("Connection OK!")
except:
    print("Error: Błąd przy łączeniu się z oscyloskopem.")
	
myScope.IO.Timeout = 15000
print("Timeout set to 15000 milliseconds.")

initialize()

get_spectrum()

# do something
# get_spectrum()
# return spectrum, do something else
# [...]

print("\n\nEnd of program\n")