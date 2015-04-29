import msvcrt
import time
import struct

from UDP_SOCK import UDP


speedValue = 75
movingForward = 1

addr = "192.168.1.13"

def test(addr, msg):
    print "Test"
    print addr
    print ord(msg[0])

    if(verifyMsg(msg)):
        print "True"

    print "Length: " + str(len(msg))

    for i in msg:
        print ord(i)

    print getTimeStamp(msg)

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

#Stops the motors that move robot. Parks the robot
#def park():
#    ser.write(chr(0x84) + chr(0x00) + chr(123))
#    ser.write(chr(0x84) + chr(0x01) + chr(123))

# set up serial port
#serialPortString = '/dev/ttyACM1'
#ser = serial.Serial(serialPortString, 9600)
#ser.open()
#ser.write(chr(0xa1))
#ser.timeout = 0.1

#connect to arm control arduino
#arms = serial.Serial('/dev/ttyACM2', 115200, timeout=1, writeTimeout=1)
#arms.open()
time.sleep(0.5) # must allow time for arduino to initialize

#if(ser.read()):
#    print '\nSuccessfully connected to ', serialPortString
#else:
#    ser.close()
#    serialPortString = '/dev/ttyACM0'
#    ser = serial.Serial(serialPortString, 9600)
#    ser.open()
#    print '\nSuccessfully connected to ', serialPortString

#ser.timeout = None
#arms.timeout = None

#def move():
#    ser.write(chr(0xff) + chr(0x00) + chr(speedValue))
#    ser.write(chr(0xff) + chr(0x01) + chr(speedValue))

# function for getting the key typed
def getkey():
    c = None
    c = msvcrt.getch()

    return c

# start main program
if __name__ == '__main__':
    global addr
    sock = UDP(5000)
    sock.startReceive(test)
    print '\nNAVIGATION CONTROLS:'
    print 'w-a-s-d moves the robot, p: pause/park, n: quit'
    print 'i: speed up, k: slow down'
    print 'q curves forward left, e curves forward right'
    print 'z curves backward left, c curves backward right\n'
    print 'MINING CONTROLS:'
    print 'h: mine (push arms down, close shell, pick arms up)'
    print 'y: dump (lift arms up, open shell, bring arms down)\n'

    while 1:
        c = getkey()

        if c == 'n':
            # quit
            # stop the robot
            response = raw_input("Would you like to shutdown?(y/n): ")
            if(response and (response[0] == 'y' or response[0] == "Y")):
                sock.send(createMoveMsg(0x0C), addr)
                # send the stop command
                sock.send(createMsg(0xF1), addr)
                sock.close()
                break
            else:
                print "Shutdown Aborted"

        elif c == 'w':
            # go forward
            sock.send(createMoveMsg(0x00), addr)

        elif c == 'a':
            # go left in place
            sock.send(createMoveMsg(0x02), addr)

        elif c == 'q': #curve left forward
            sock.send(createMoveMsg(0x04), addr)

        elif c == 'z': #curve left reverse
          sock.send(createMoveMsg(0x05), addr)

        elif c == 's':
            # go backwards
            sock.send(createMoveMsg(0x01), addr)
        elif c == 'd':
            # go right in place
            sock.send(createMoveMsg(0x03), addr)

        elif c == 'e': #curve right forward
           sock.send(createMoveMsg(0x06), addr)

        elif c == 'c': #curve right reverse
            sock.send(createMoveMsg(0x07), addr)

        elif c == 'p': #park
            sock.send(createMoveMsg(0x0C), addr)

#        elif c == 'y':
#            sock.send(createMsg(0x0B), addr)

#        elif c == 'h':
#            sock.send(createMsg(0x0A), addr)

        elif c == '=':
            #speed up
            sock.send(createMoveMsg(0x08), addr)

        elif c == '-':
            #slow down
            sock.send(createMoveMsg(0x09), addr)
        elif c == 'i':
            #rasie arm
            sock.send(createMoveMsg(0x0D), addr)
        elif c == 'k':
            #lower arm
            sock.send(createMoveMsg(0x0E), addr)
        elif c == 'y':
            #raise second arm
            sock.send(createMoveMsg(0x0F), addr)
        elif c == 'h':
            #lower second arm
            sock.send(createMoveMsg(0x10), addr)
        elif c == '[':
            #winch
            sock.send(createMoveMsg(0x15), addr)
        elif c == ']':
            #winch
            sock.send(createMoveMsg(0x16), addr)
        elif c == 'u':
            #Left Actuator Up
            sock.send(createMoveMsg(0x11), addr)
        elif c == 'j':
            #Left Actuator down
            sock.send(createMoveMsg(0x13), addr)
        elif c == 'o':
            #Right Actuator Up
            sock.send(createMoveMsg(0x12), addr)
        elif c == 'l':
            #Right Actuator down
            sock.send(createMoveMsg(0x14), addr)


        #sleep for half a second
        time.sleep(0.1)