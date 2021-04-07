import visa
import Rigol1000z

rm = visa.ResourceManager()

# We are connecting the oscilloscope through USB here.
# Only one VISA-compatible instrument is connected to our computer,
# thus the first resource on the list is our oscilloscope.
# You can see all connected and available local devices calling
#
# print(rm.list_resources())
#
osc_resource = rm.open_resource(rm.list_resources()[0])

osc = Rigol1000z.Rigol1000z(osc_resource)

# Change voltage range of channel 1 to 50mV/div.
osc[1].set_vertical_scale_V_div(50e-3)

# Stop the scope.
osc.stop()

# Take a screenshot.
osc.get_screenshot('screenshot.png', 'png')

# Capture the data sets from channels 1--4 and
# write the data sets to their own file.
for c in range(1,5):
    osc[c].get_data('raw', 'channel%i.dat' % c)