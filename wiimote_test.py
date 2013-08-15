
import cwiid
import time

print 'Press 1+2 on your Wiimote now'
wm=cwiid.Wiimote()

for i in range(16):
    wm.led = i
    wm.rumble = 1-i%2
    time.sleep(.5)

#Enable button reporting
wm.rpt_mode = cwiid.RPT_BTN
print wm.state

# Enable button and accel reporting
wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
print wm.state


while True:
    wm.rumble = (wm.state['acc'][0] < 126)
    if wm.state['buttons'] & cwiid.BTN_A:
    wm.led = (wm.state['led'] + 1) % 16
    time.sleep(.2)
