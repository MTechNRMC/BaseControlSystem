import time
import struct

#interpretor function
def intrp(addr, msg):

    while len(msg) > 0:
     #   if(verifyMsg(msg)):
        for x in range(0, len(msg)):
            #get the command
            cmd = msg.pop(0)
            print cmd
            if(cmd == 0x00):
                #Move forward
                print "Test"
            elif(cmd == 0x01):
                #Move backward
                print "Test1"
            elif(cmd == 0x02):
                #Rot Left
                print "Test2"
            elif(cmd == 0x03):
                #Rot Right
                print "Test3"
            elif(cmd == 0x04):
                #Curve Forward Left
                print "Test4"
            elif(cmd == 0x05):
                #Curve Backward Left
                print "Test5"
            elif(cmd == 0x06):
                #Curve Forward Right
                print "Test6"
            elif(cmd == 0x07):
                #Curve Backward Right
                print "Test7"
            elif(cmd == 0x08):
                #Increase Speed
                print "Test8"
            elif(cmd == 0x09):
                #Decrease Speed
                print "Test9"
            elif(cmd == 0x0A):
                #Dig
                print "Test10"
            elif(cmd == 0x0B):
                #Dump
                print "Test11"
            elif(cmd == 0x0C):
                #Stop Movement
                print "Test12"
            elif(cmd == 0xEF):
                #Resume
                print "Test13"
            elif(cmd == 0xF0):
                #Start
                print "Test14"
            elif(cmd == 0xF1):
                #Stop
                print "Test15"
            elif(cmd == 0xF2):
                #Manual Control
                print "Test16"

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

    #pad the msg
    for x in range(0, 3):
        msg += chr(0)

    msg += genCheckSum(msg)

    return msg

#get the info on the current state of the bump sensors
def getBumpInfo(msg):
    return msg[1:2]

#create a packet that sends the current set speed of the left and right track
def createTrackSpeedMsg(lTrack, rTrack):
    msg = chr(0xF8) + chr(lTrack) + chr(rTrack)
    #add the padding so it is 6 byts in length
    for x in range(0, 2):
        msg += chr(0)
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

def createMsg(code):
    msg = chr(code)
    #pad the msg
    for x in range(0, 4):
        msg += chr(0)

    #gen check sum
    msg += genCheckSum(msg)
    return msg



print "Length: " + str(len(createMsg(0xFF)))

for i in createMsg(0xFF):
    print ord(i)