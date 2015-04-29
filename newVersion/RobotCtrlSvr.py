import termios, sys, os
import serial
import time
import struct

from UDP_SOCK import UDP

# set up serial port
serialPortString = '/dev/ttyACM1'
ser = serial.Serial(serialPortString, 9600)
ser.open()
ser.write(chr(0xa1))
ser.timeout = 0.1

movingForward = 1
speedValue = 75

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
def getTimeStamp(msg):
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
	ser.write(chr(0xff) + chr(0x00) + chr(123))     #Left Drive?
	ser.write(chr(0xff) + chr(0x01) + chr(123))     #Right Drive?
	ser.write(chr(0xff) + chr(0x02) + chr(123))     #Left Actuator
	ser.write(chr(0xff) + chr(0x03) + chr(123))     #Right Actuator
	ser.write(chr(0xff) + chr(0x04) + chr(123))     #Bucket Actuator
	ser.write(chr(0xff) + chr(0x05) + chr(123))     #Winch Drive

# Move Forward
def func_moveForward():
	park()
	movingForward = 1
	speedValue = 50
	move()

# Rotate Left
def func_rotateLeft():
	park()
	ser.write(chr(0xff) + chr(0x00) + chr(254))
	ser.write(chr(0xff) + chr(0x01) + chr(1))

# Curve Left Forward
def func_curveLeftForward():
	park()
	ser.write(chr(0xff) + chr(0x00) + chr(75))
	ser.write(chr(0xff) + chr(0x01) + chr(0))

# Curve Left Reverse
def func_curveLeftReverse():
	park()
	ser.write(chr(0xff) + chr(0x00) + chr(179))
	ser.write(chr(0xff) + chr(0x01) + chr(254))

# Curve Right Reverse
def func_curveRightReverse():
	park()
	ser.write(chr(0xff) + chr(0x01) + chr(179))
	ser.write(chr(0xff) + chr(0x00) + chr(254))

# Reverse
def func_reverse():
	park()
	movingForward = 0
	speedValue = 204
	move()

# Rotate Right
def func_rotateRight():
	park()
	ser.write(chr(0xff) + chr(0x00) + chr(1))
	ser.write(chr(0xff) + chr(0x01) + chr(254))

# Curve Right Forward
def func_curveRightForward():
	park()
	ser.write(chr(0xff) + chr(0x00) + chr(0))
	ser.write(chr(0xff) + chr(0x01) + chr(75))

# Move (this is called by speedUp and slowDown)
def move():
	ser.write(chr(0xff) + chr(0x00) + chr(speedValue))
	ser.write(chr(0xff) + chr(0x01) + chr(speedValue))

# Slow Down
def func_slowDown():
	global speedValue
	if (movingForward == 1):
		if ( speedValue <= 50):
			speedValue = speedValue + 25
	else:
		if (speedValue >= 204):
			speedValue = speedValue - 25
	move()

# Speed Up
def func_speedUp():
	global speedValue
	if (movingForward == 1):
		if (speedValue >= 25):
			speedValue = speedValue - 25
	else:
		if (speedValue <= 229):
			speedValue = speedValue + 25
	move()

# Dig
#def func_dig():
#	park()
#	arms.write('e')
#	out = ''
#	time.sleep(0.5)
#	while (arms.inWaiting() > 0):
#		out += arms.read(1)
#		#print out
#	arms.write('e')
#	while (arms.read() != 'p'):
#		time.sleep(.01)

# Take a dump
#def func_dump():
#	park()
#	arms.write('d')
#	out = ''
#	time.sleep(0.5)
#	while (arms.inWaiting() > 0):
#		out += arms.read(1)
		#print out
#	arms.write('d')
#	while (arms.read() != 'p'):
#		time.sleep(.01)

#Bring main arms up
def func_mainArmsUp():
	park()
	ser.write(chr(0xff) + chr(0x02) + chr(254))     #Left Actuator
	ser.write(chr(0xff) + chr(0x03) + chr(254))     #Right Actuator

#Bring main arms down
def func_mainArmsDown():
	park()
	ser.write(chr(0xff) + chr(0x02) + chr(0))     #Left Actuator
	ser.write(chr(0xff) + chr(0x03) + chr(0))     #Right Actuator

#Left Actuator Up
def func_leftActuatorUp():
	park()
	ser.write(chr(0xff) + chr(0x02) + chr(254))

#Left Actuator Down
def func_leftActuatorDown():
	park()
	ser.write(chr(0xff) + chr(0x02) + chr(0))

#Right Actuator Up
def func_rightActuatorUp():
	park()
	ser.write(chr(0xff) + chr(0x03) + chr(254))

#Right Actuator Down
def func_rightActuatorDown():
	park()
	ser.write(chr(0xff) + chr(0x03) + chr(0))

#Scondary Actuator Up
def func_bucketActuatorUp():
	park()
	ser.write(chr(0xff) + chr(0x04) + chr(254))

#Scondary Actuator down
def func_bucketActuatorDown():
	park()
	ser.write(chr(0xff) + chr(0x04) + chr(0))

#forward winch
def func_forwardWinch():
	park()
	ser.write(chr(0xff) + chr(0x05) + chr(254))

#reverse winch
def func_reverseWinch():
	park()
	ser.write(chr(0xff) + chr(0x05) + chr(0))

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
			#Move forward
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_moveForward()
			time.sleep(.1)
			park()
#			print("Move Forward")

			#clear the buffer of all codes with same time stamp
#                while len(msg) > 0 and lastTimeStamp >= getTimeStamp(msg) and lastCode == msg[0]:
#                    for x in range(0, 5) and len(msg) > 0:
					#clear the packet
#                        msg.pop[0]

		elif(ord(msg[0]) == 0x01):
			#Move backward
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_reverse()
			time.sleep(.1)
			park()
#			print("Move Backward")

		elif(ord(msg[0]) == 0x02):
			#Rot Left
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_rotateLeft()
			time.sleep(.1)
			park()
#			print("Rot Left")

		elif(ord(msg[0]) == 0x03):
			#Rot Right
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_rotateRight()
			time.sleep(.1)
			park()
#			print("Rot Right")

		elif(ord(msg[0]) == 0x04):
			#Curve Forward Left
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_curveLeftForward()
			time.sleep(.1)
			park()
#			print("Forward Left")

		elif(ord(msg[0]) == 0x05):
			#Curve Backward Left
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_curveLeftReverse()
			time.sleep(.1)
			park()
#			print("Backward Left")

		elif(ord(msg[0]) == 0x06):
			#Curve Forward Right
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_curveRightForward()
			time.sleep(.1)
			park()
#			print("Forward Right")

		elif(ord(msg[0]) == 0x07):
			#Curve Backward Right
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_curveRightReverse()
			time.sleep(.1)
			park()
#			print("Backward Right")

		elif(ord(msg[0]) == 0x08):
			#Increase Speed
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_speedUp()
			time.sleep(.1)
			park()
#			print("Increase Speed")

		elif(ord(msg[0]) == 0x09):
			#Decrease Speed
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_slowDown()
			time.sleep(.1)
			park()
#			print("Decrease Speed")

		elif(ord(msg[0]) == 0x0A):
			#Dig
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
#			func_dig()
			time.sleep(.1)
			park()
#			print("Dig")

		elif(ord(msg[0]) == 0x0B):
			#Dump
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
#			func_dump()
			time.sleep(.1)
			park()
#			print("Dump")

		elif(ord(msg[0]) == 0x0C):
			#Stop Movement
			lastTimeStamp = 0  #reset the time stamp
			park()
#			print("Stop")

		elif(ord(msg[0]) == 0x0D):
			#Main Arm Up
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_mainArmsUp()
			time.sleep(.1)
			park()
#			print("Main Arm Up")

		elif(ord(msg[0]) == 0x0E):
			#Main Arm Down
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_mainArmsDown()
			time.sleep(.1)
			park()
#			print("Main Arm Down")

		elif(ord(msg[0]) == 0x0F):
			#Bucket Actuator Out
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_bucketActuatorUp()
			time.sleep(.1)
			park()
#			print("Bucket Actuator Out")

		elif(ord(msg[0]) == 0x10):
			#Bucket Actuator In
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_bucketActuatorDown()
			time.sleep(.1)
			park()
#			print("Bucket Actuator In")

		elif(ord(msg[0]) == 0x11):
			#L Actuator Up
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_leftActuatorUp()
			time.sleep(.1)
			park()
#			print("L Actuator Up")

		elif(ord(msg[0]) == 0x12):
			#R Actuator Up
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_rightActuatorUp()
			time.sleep(.1)
			park()
#			print("R Actuator Up")

		elif(ord(msg[0]) == 0x13):
			#L Actuator Down
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_leftActuatorDown()
			time.sleep(.1)
			park()
#			print("L Actuator Down")

		elif(ord(msg[0]) == 0x14):
			#R Actuator Down
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_rightActuatorDown()
			time.sleep(.1)
			park()
#			print("R Actuator Down")

		elif(ord(msg[0]) == 0x15):
			#Winch Forward
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_forwardWinch()
			time.sleep(.1)
			park()
#			print("Winch Forward")

		elif(ord(msg[0]) == 0x16):
			#Winch Reverse
			lastCode = msg[0]
			lastTimeStamp = getTimeStamp(msg)
			func_reverseWinch()
			time.sleep(.1)
			park()
#			print("Winch Reverse")

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