import time
import struct

from Socket.UDP_SOCK import UDP


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

# Park
def park():
    ser.write(chr(0xff) + chr(0x00) + chr(123))
    ser.write(chr(0xff) + chr(0x01) + chr(123))

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
	if (movingForward == 1):
	    if (speedValue <= 50):
	        speedValue = speedValue + 25
	else:
	    if (speedValue >= 204):
	    	speedValue = speedValue - 25
	move()

# Speed Up
def func_speedUp():
	if (movingForward == 1):
	    if (speedValue >= 25):
			speedValue = speedValue - 25
	else:
		if (speedValue <= 229):
			speedValue = speedValue + 25
    move()

# Dig
def func_dig():
    park()
	arms.write('e')
	out = ''
	time.sleep(0.5)
	while (arms.inWaiting() > 0):
	    out += arms.read(1)
		#print out
	arms.write('e')
    while (arms.read() != 'p'):
        time.sleep(.01)

# Take a dump
def func_dump():
	park()
	arms.write('d')
	out = ''
	time.sleep(0.5)
	while (arms.inWaiting() > 0):
        out += arms.read(1)
        #print out
	arms.write('d')
    while (arms.read() != 'p'):
        time.sleep(.01)

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

        elif(ord(msg[0]) == 0x02):
            #Rot Left
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_rotateLeft()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x03):
            #Rot Right
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_rotateRight()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x04):
            #Curve Forward Left
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_curveLeftForward()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x05):
            #Curve Backward Left
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_curveLeftReverse()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x06):
            #Curve Forward Right
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_curveRightForward()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x07):
            #Curve Backward Right
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_curveRightReverse()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x08):
            #Increase Speed
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_speedUp()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x09):
            #Decrease Speed
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_slowDown()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x0A):
            #Dig
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_dig()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x0B):
            #Dump
            lastCode = msg[0]
            lastTimeStamp = getTimeStamp(msg)
            func_dump()
            time.sleep(.1)
            park()

        elif(ord(msg[0]) == 0x0C):
            #Stop Movement
            lastTimeStamp = 0  #reset the time stamp
            park()

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