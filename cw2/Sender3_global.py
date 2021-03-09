import socket
import sys
import time 
import select
import threading
import queue


#TODO
#Retransmitting isnt accurate, need to work out why
#need to work out how to end the sender

#constants
PAYLOAD_SIZE = 1024
HEADER_SIZE = 3
ACK_SIZE = 2

#global variables
t = None
base = 1
seq_num = 1
c = threading.Condition()


def timer():
    start = round(time.time() * 1000)
    while True:
        yield round(time.time() * 1000) - start



#idk if this is even a good idea but im cba thinking about it rn
def ack_thread(sock):

    print("Ack thread started")
    while True:
        global t
        global base
        global seq_num

        r_buf = sock.recvfrom(2)#recv 2 bytes for ack

        ack = r_buf[0]
        ack = int.from_bytes(ack, "big")

        #print("received ack: %d" % ack)
        
        c.acquire()
        #CRITICAL SECTION
        base = ack+1
 
        if (ack == (seq_num-1)):#ack should be for the last packet we sent

            if (base == seq_num):
                t = None
            else:
                t = timer()
        #CRITICAL SECTION OVER
            
        c.release()
        




def make_packet(i, file_buf):

    seq = i.to_bytes(2, byteorder='big')#first 2 bytes for sequence number
    
    end = False

    #set eof flag
    eof = (0).to_bytes(1, byteorder='big')

    print("seq num: %d"% i)
    print(len(file_buf))
    if (len(file_buf) < PAYLOAD_SIZE): 
        end = True
        eof = (1).to_bytes(1, byteorder='big')

    #construct packet
    s_buf = bytearray()# need a new buffer for every packet
    s_buf[0:0] = seq
    s_buf[2:2] = eof
    s_buf[3:3] = bytearray(file_buf)


    #return packet and seqeuence number of packet
    return s_buf, end



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
    N = int(argv[5]) #window size

    #need queues for all the shared variables

    global t
    global base
    global seq_num

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    

    start = time.time()#performance measuring

    f = open(FILE, 'rb')
    file_buf = f.read(PAYLOAD_SIZE)

    #thread for recieving acks
    t1 = threading.Thread(target=ack_thread, args=(sock,))
    t1.start()

    print("Sender Thread Started")
    while (True): #while the file can still be read 

        #print("base: %d"% base)
        #print("seq_num: %d"% seq_num)

        if (seq_num < (base+N)):
            s_buf, end = make_packet(seq_num, file_buf)
            sock.sendto(s_buf, (HOST, PORT)) #send data


            
            if (base == seq_num): #first packet in window
                t = timer()

            #CRITICAL SECTION
            c.acquire()
            seq_num += 1 
            c.release()
            #CRITICAL SECTION OVER

            file_buf = f.read(PAYLOAD_SIZE)

            
        
        #check timer
        delta_t = next(t)
        if (delta_t >= TIMEOUT):#if we time out, resend all unacked packets in window

            t = timer()

            i = base
            f.seek(i*(PAYLOAD_SIZE-1))
            
            for i in range(i, seq_num):
                file_buf = f.read(PAYLOAD_SIZE)
                s_buf, end = make_packet(i, file_buf)
                sock.sendto(s_buf, (HOST, PORT))

            file_buf = f.read(PAYLOAD_SIZE)
            

        


        #time.sleep(1)

    print("Finished")
    #end
    t1.join()    
    f.close()    


    delta = time.time() - start
    tp = round((file_size/delta)/1000)

    output = "{} {}".format(retries, tp) 
    print (output)


if __name__ == "__main__": 
    main(sys.argv)


