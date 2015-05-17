import termios, sys, os
import serial
import time
import struct

from UDP_SOCK import UDP

# set up serial port
serialPortString = '/dev/ttyACM0'
ser = serial.Serial(serialPortString, 9600)
ser.open()
ser.write(chr(0xa1))
ser.timeout = 0.1

movingForward = 1
maxSpeedValue = 63  #max speed for the drive motors
speedValue = maxSpeedValue
neutralPoint = 127  #might have to change to 123

auto = False
lastCode = 0x00
lastTimeStamp = 0

#socket for serial communication
s = UDP(5000)

#******************************************************************************
# Functions for creating packets and retrieving data from packets
#******************************************************************************

#get a time stamp
def genTimeStamp():
	return int(time.time())

#gen a check sum for the msg
def genCheckSum(msg):
	chkSum = 0x00

	for char in msg:
		chkSum ^= ord(char)

	return chr(chkSum)

#encode an int
def encodeInt(num):
	return struct.pack("!i", int(num))

#create a move msg
def createMoveMsg(code):
	msg = chr(code)+encodeInt(genTimeStamp())
	# append the checksum
	msg += genCheckSum(msg)

	return msg

#get the timestamp from a move msg
def getMoveMsg(msg):
	print ("msg: " + struct.unpack("!i", msg[1:5])[0])  #debugging
	return struct.unpack("!i", msg[1:5])[0]

# verify the msg checksum
def verifyMsg(msg):
	chckSum = msg[len(msg)-1]

	if(genCheckSum(msg[0:len(msg)-1]) == chckSum):
		return True

	return False

#create a msg containing data on what bump sensors have been hit
def createBumpMsg(snsrInfo):
	msg = chr(0xF7) + chr(snsrInfo)
	msg += genCheckSum(msg)

	return msg

#get the info on the current state of the bump sensors
def getBumpInfo(msg):
	return msg[1:2]

#create a packet that sends the current set speed of the left and right track
def createTrackSpeedMsg(lTrack, rTrack):
	msg = chr(0xF8) + chr(lTrack) + chr(rTrack)
	msg += genCheckSum(msg)

	return msg

#get the current set speed of the left and right tracks from the message
def getTrackSpeed(msg):
	spd = []
	spd[0] = ord(msg[1:2])
	spd[1] = ord(msg[2:3])

	return spd

#creare a msg to send back the rot of the arm mortars
#NOTE: packet size now 6 instead of 4 bytes
def createArmRotMsg(code, armRot):
	msg = chr(code) + encodeInt(armRot)
	msg += genCheckSum(msg)

	return msg

#get the rot of the arm motors from
def getArmRot(msg):
	return struct.unpack("!i", msg[1:5])[0]

# Park - Stops all motors
def park():
	ser.write(chr(0xff) + chr(0x00) + chr(neutralPoint))     #Left Drive
	ser.write(chr(0xff) + chr(0x01) + chr(neutralPoint))     #Right Drive
	ser.write(chr(0xff) + chr(0x02) + chr(neutralPoint))     #Left Actuator
	ser.write(chr(0xff) + chr(0x03) + chr(neutralPoint))     #Right Actuator
	ser.write(chr(0xff) + chr(0x04) + chr(neutralPoint))     #Bucket Actuator
	ser.write(chr(0xff) + chr(0x05) + chr(neutralPoint))     #Winch Drive

# set a motor to move forward or backward
def setMotor(motor, msg):
	#set the correct speed value according to motor
	if(motor == 0 or motor == 1):
		speed = speedValue
	else:
		speed = neutralPoint

	#get the direction to move the motor
	dirc = (msg >> (2*motor)) & 3

	print("dirc: " + dirc)

	#set the velocity
	if(dirc == 0x01):
		vel = neutralPoint+speedValue #forward
	elif(dir == 0x02):
		vel = neutralPoint-speedValue #backward
	else:
		vel = neutralPoint #stop

	print("vel: " + vel)

	#send the msg to the servo controller
	ser.write(chr(0xff)+chr(motor)+chr(vel))

# set all motors to move
def setMotorsAll(msg):
	for i in range(0, 6):
		setMotor(i, msg)

# Slow Down
def func_slowDown():
	global speedValue
	if(speedValue >= (neutralPoint-maxSpeedValue)):
		pass

# Speed Up
def func_speedUp():
	global speedValue
	if(speedValue <= (neutralPoint+maxSpeedValue)):
		pass

####################################################################################################
#misc functions
####################################################################################################


####################################################################################################
#Interpreter Function
####################################################################################################

def intrp(addr, msg):

#    while len(msg) > 0:
	if(verifyMsg(msg)):
		if(ord(msg[0]) == 0x00):
			#set motors
			lastCode = msg[0]
			setMotorsAll(getMoveMsg(msg))
			print("move")

		elif(ord(msg[0]) == 0x0C):
			#Stop Movement
			lastTimeStamp = 0  #reset the time stamp
			park()
#			print("Stop")

		elif(ord(msg[0]) == 0xEF):
			#Resume
			pass

		elif(ord(msg[0]) == 0xF0):
			#Start
			pass

		elif(ord(msg[0]) == 0xF1):
			#Stop
			pass

		elif(ord(msg[0]) == 0xF2):
			#Manual Control
			pass
			auto = False
			#send the confirm a few times to assure receiving
			#for x in range(0, 5):
			#    s.send(0xF2,addr)

if __name__ == '__main__':
	s.startReceive(intrp)
	while 1:
		time.sleep(5)
		pass
