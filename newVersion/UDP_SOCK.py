import socket
import thread
import time

# A class for communication over a network using UDP
# @author Josh Lee <jlee1@mtech.edu>
class UDP:
    # A constructor that uses a socket created outside of the class
    # @param sock[in] A UDP socket
    def __init__(self, sock):
        self.sct = sock

    # A constructor that creates a new UDP socket on the specified port with a default buffer size
    # and timeOut unless otherwise specified
    # @param port[in] The port the socket will listen on
    # @param buffer_size[in] The size of the buffer the socket will use defaults to 1024
    # @param timeOut[in] The amount of time in seconds before a receive will fail defaults to 15s
    def __init__(self, port, buffer_size = 6, timeOut = 15):
        # assign the port and buffer size to vars in the class
        self.port = port
        self.bufferSize = buffer_size

        try:
            # create a UDP socket that connects through ip
            self.sct = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sct.bind(("", port))           # bind the socket to the port and set to listen for all IP addr
            self.sct.settimeout(timeOut)        # Set the timeout for the socket
        # the socket could not be created
        except socket.error, (value,message):
            if(self.sct):
                self.sct.close()
            print "[ERR]Socket Failure: " + message #temp for errors will replace later

    # Shutdown and dispose of the socket. To ensure proper shutdown close will sleep for the timeout+1 to allow the
    # receive to timeout and the thread to exit gracefully
    # @return True if successful
    def close(self):
        try:
            self.stopReceive()                  #Set for the receive to stop next timout ending the thread
            self.sct.shutdown(socket.SHUT_RDWR) #send the shutdown signal NOTE not sure if this is useful for UDP
            time.sleep(self.sct.gettimeout()+1) #wait for one second longer than the timeout to make sure thread gracefully terminates
            self.sct.close()                    #close the socket
        # socket failed to close
        except socket.error, (value,message):
            print "[ERR]Socket Failure: " + message #temp for errors will replace later
            return False
        return True

    # Starts a new thread to receive messages
    # @param func[in] The handler function for handling received messages. The function that is passed should only
    # take two argument, address of the sender and the message received
    # @return True if successful
    def startReceive(self, func):
        self.rx = True                          # set to true to continually receive messages
        #create a rx thread
        try:
            thread.start_new_thread(self.receive, (func,))  # start receiving on a new thread
        # Thread failed to start
        except thread.error, (value,message):
            print "[ERR]Thread Failure: " + message    #temp for errors will replace later
            return False
        return True

    # A function to stop receiving messages NOTE: takes effect next timeout
    def stopReceive(self):
        self.rx = False

    # A function to send a message to a specified address on the port the socket is listening on
    # @param msg[in] The message to send
    # @param addr[in] The ip address of the receiver
    # @return True on success
    def send(self, msg, addr):
        try:
            # check if a sct was created
            if self.sct:
                self.sct.sendto(msg, (addr, self.port)) # Send the msg
            else:
                return False
        # Send failed
        except socket.error, (value,message):
            print "[ERR]Socket Failure: " + message #temp for errors will replace later
            return False
        return True

    def broadcast(self, msg):
        self.send(msg, "255.255.255.255")

# DO NOT UNCOMMENT WIP
#    def send(self, msg, addr, port):
#       try:
#            self.sct.sendto(msg, (addr, port))
#        except:
#            print "[ERR]Socket Failure: Message failed to send" #temp for errors will replace later
#            return False
#        return True

    # A function that continually listens for messages
    # NOTE: Use startReceive not receive. Receive is a blocking function
    # @param func[in] The handler function for handling received messages. The function that is passed should only
    # take two argument, address of the sender and the message received
    def receive(self, func):
        #continue receiving until rx is set to false and a socket was created
        while self.rx and self.sct:
            try:
                message, addr = self.sct.recvfrom(self.bufferSize)  # listen for messages
                #call the handler function
                func(addr, message)
            # A timeout occurred just ignore and carry on
            except socket.timeout:
                pass
            # Received failed print the error and retry
            except socket.error, (value,message):
                print "[ERR]Socket Failure: " + message #temp for errors will replace later