import termios, sys, os
import serial
import time

# set up serial port
serialPortString = '/dev/ttyACM1'
ser = serial.Serial(serialPortString, 9600)
ser.open()
ser.write(chr(0xa1))
ser.timeout = 0.1

speedValue = 75
movingForward = 1

def move():
    ser.write(chr(0xff) + chr(0x00) + chr(speedValue))
    ser.write(chr(0xff) + chr(0x01) + chr(speedValue))

def slowDown():
	#slow down
	if (movingForward == 1):
	    if (speedValue <= 50):
	        speedValue = speedValue + 25
	else:
	    if (speedValue >= 204):
	    	speedValue = speedValue - 25
	move()

def speedUp():
    #speed up
	if (movingForward == 1):
	    if (speedValue >= 25):
			speedValue = speedValue - 25
	else:
		if (speedValue <= 229):
			speedValue = speedValue + 25
    move()

def dig():
    # excavate/dig
    #send bucket arduino a 'e' for excavate
    park()
	arms.write('p')
	out = ''
	time.sleep(0.5)
	while (arms.inWaiting() > 0):
	    out += arms.read(1)
		#print out
	arms.write('p')

def dump():
    # dump into bin
    #send bucket arduino a 'd' for dump
	park()
	arms.write('d')
	out = ''
	time.sleep(0.5)
	while (arms.inWaiting() > 0):
        out += arms.read(1)
        #print out
	arms.write('d')

def curveRightReverse():
    #curve right reverse
    park()
    ser.write(chr(0xff) + chr(0x00) + chr(254))
    ser.write(chr(0xff) + chr(0x01) + chr(179))