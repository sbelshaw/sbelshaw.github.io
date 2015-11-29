import time, sys, signal, atexit
import pyupm_mma7660 as upmMMA7660
import rtmidi_python as rtmidi

# Instantiate an MMA7660 on I2C bus 0
myDigitalAccelerometer = upmMMA7660.MMA7660(
					upmMMA7660.MMA7660_I2C_BUS, 
					upmMMA7660.MMA7660_DEFAULT_I2C_ADDR);

# place device in standby mode so we can write registers
myDigitalAccelerometer.setModeStandby()

# enable 64 samples per second
myDigitalAccelerometer.setSampleRate(upmMMA7660.MMA7660.AUTOSLEEP_64)

# place device into active mode
myDigitalAccelerometer.setModeActive()

x = upmMMA7660.new_intp()
y = upmMMA7660.new_intp()
z = upmMMA7660.new_intp()

midi_out = rtmidi.MidiOut() # get midi and open port
midi_out.open_port(0)

midi_out.send_message([0xC0, 92]) # programme change - bowed glass
midi_out.send_message([0xB0, 65, 127]) # portamento on
midi_out.send_message([0xB0, 5, 30]) # portamento time can be varied

try:
	
	while True:
		
		myDigitalAccelerometer.getRawValues(x, y, z)
		
		rawNote = upmMMA7660.intp_value(x) # reads left to right value
		rawVol = upmMMA7660.intp_value(z) # reads backwards and forwards value
		
		if rawNote < -25: # avoids going out of range
			rawNote = -25
		if rawVol < -25:
			rawVol = -25
			
		note = int((rawNote + 25) * 2.4) # value ranges from -25 to 25 so this to 
										# convert to midi value on range 0 - 127
		vol = int((rawVol + 25) * 2.4)
		
		# print 'note', note, 'volume', vol # only if you need to see what's happening
	
		midi_out.send_message([0x90, note, vol])
		time.sleep(.1) # can be varied to taste
		midi_out.send_message([0x80, note, vol])

except KeyboardInterrupt:
	
	midi_out.send_message([0xB0, 120, 0]) # all sounds off
	midi_out.send_message([0xB0, 65, 0]) # portamento off
	del midi_out
	
