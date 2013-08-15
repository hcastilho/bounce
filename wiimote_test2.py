
import cwiid
import time

print 'Press 1+2 on your Wiimote now'
tic=tac=time.clock()
controllers=[]
while tac-tic<5
    controllers.append(cwiid.Wiimote()) # What is the timeout for Wiimote()
    tac=time.clock()


for wm in controllers:
    wm.enable(cwiid.FLAG_MOTIONPLUS)
    # wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC | cwiid.RPT_MOTIONPLUS | cwiid.RPT_NUNCHU
    wm.rpt_mode = cwiid.RPT_BTN | cwiid.RPT_ACC
    print wm.state


    while True:
        wm.rumble = (wm.state['acc'][0] < 126)
        if wm.state['buttons'] & cwiid.BTN_A:
        wm.led = (wm.state['led'] + 1) % 16
        time.sleep(.2)
