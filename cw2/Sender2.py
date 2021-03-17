#Greig Huth 
#s1532620

import socket
import sys
import time 
import select

PAYLOAD_SIZE = 1024
HEADER_SIZE = 3
ACK_SIZE = 2

def timer():
    start = round(time.time() * 1000)
    while True:
        yield round(time.time() * 1000) - start


def main(argv):

    #performance tracking
    total     = 0   #total number of packets sent
    retries   = 0   #number of retransmissions
    file_size = 0   #file size in bytes

    #unpack arguments
    HOST = argv[1]
    PORT = int(argv[2])
    FILE = argv[3].encode('utf-8')
    TIMEOUT = int(argv[4])

    #file 
    f = open(FILE, 'rb')
    
    #set up socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #start reading file
    file_buf = f.read(PAYLOAD_SIZE)
    
    #start timer for performance measuring
    start = time.time()

    i = 0 # sequence number
    while (file_buf): 

        seq = i.to_bytes(2, byteorder='big')#first 2 bytes for sequence number
        eof = (0).to_bytes(1, byteorder='big')#3rd byte for EOF


        if (len(file_buf) < PAYLOAD_SIZE):
            eof = (1).to_bytes(1, byteorder='big')

        #print(bytearray(f.read(1024)))

        s_buf = bytearray()# need a new buffer for every packet
        s_buf[0:0] = seq
        s_buf[2:2] = eof
        s_buf[3:3] = bytearray(file_buf)

        total+= 1
        sock.sendto(s_buf, (HOST, PORT)) #send data
        t = timer() #start the timer 
        while True:

            #doesnt block when timeout is 0 out and error can just be ignored
            i_ready, o_ready, e_ready  = select.select([sock], [], [], 0)

            if i_ready:#if socket has stuff then read and check ack
                r_buf = i_ready[0].recvfrom(2) 

                ack = r_buf[0]
                #print("Reading from buffer")

                if seq == ack: #recieved correct ack
                    break # break loop and move on to next packet
                else:
                    continue # do nothing, keep waiting

            else: #else check timer
                time_passed = next(t)
                if (time_passed >= TIMEOUT):#if we have reached the timeout
                    retries += 1
                    total += 1
                    sock.sendto(s_buf, (HOST, PORT)) #retransmit
                    t = timer() # restart timer  
                    continue # go back to beginning of loop and try again

            
        
        file_size += len(file_buf)#update bytes sent

        #remember to update read buffer and sequence number
        file_buf = f.read(PAYLOAD_SIZE)
        i+=1 

    delta = time.time() - start
    tp = round((file_size/delta)/1000)

    output = "{} {}".format(retries, tp) 
    print (output)

    f.close()    

        



    

if __name__ == "__main__": 
    main(sys.argv)


