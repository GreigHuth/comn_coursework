import socket
import sys
import time 
import select
from threading import Thread, Event
import queue

#constants
PAYLOAD_SIZE = 1024
HEADER_SIZE = 3
ACK_SIZE = 2


def timer():
    start = round(time.time() * 1000)
    while True:
        yield round(time.time() * 1000) - start



#idk if this is even a good idea but im cba thinking about it rn
def ack_thread(sock, timer_q, base_q, seq_q):

    print("Ack thread started")
    while True:
        seq_num = seq_q.get()

        r_buf = sock.recvfrom(2)#recv 2 bytes for ack

        ack = r_buf[0]
        ack = int.from_bytes(ack, "big")

        print("received ack: %d" % ack)
        
        base = ack+1
        base_q.put(base)

        
        if (base == seq_num):
            t = None
        else:
            t = timer()
        
        timer_q.put(t)





def make_packet(i, file_buf):

    seq = i.to_bytes(2, byteorder='big')#first 2 bytes for sequence number
    
    end = False

    #set eof flag
    eof = (0).to_bytes(1, byteorder='big')
    if (len(file_buf) < PAYLOAD_SIZE): 
        end = True
        eof = (1).to_bytes(1, byteorder='big')

    #construct packet
    s_buf = bytearray()# need a new buffer for every packet
    s_buf[0:0] = seq
    s_buf[2:2] = eof
    s_buf[3:3] = bytearray(file_buf)

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

    base_q = queue.Queue() #needed for sharing variables
    base = 1 # base number for the window, is accessed by both threads
    base_q.put(base)

    seq_q = queue.Queue()
    seq_num = 1 # sequence number
    seq_q.put(seq_num)

    timer_q = queue.Queue()
    t = None
    timer_q.put(t)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    

    start = time.time()#performance measuring

    f = open(FILE, 'rb')
    file_buf = f.read(PAYLOAD_SIZE)

    #thread for recieving acks
    t1 = Thread(target=ack_thread, args=(sock, timer_q, base_q, seq_q))
    t1.start()

    print("Sender Thread Started")
    while (file_buf): #while the file can still be read 
        print("test")
        base = base_q.get()
        print("test")
        seq_num = seq_q.get()
        print("test")
        print("seq_num: %d"% seq_num)

        end = False

        if (seq_num < (base+N)):
            s_buf, end = make_packet(seq_num, file_buf)
            sock.sendto(s_buf, (HOST, PORT)) #send data

            if (base == seq_num): #first packet in window
                t = timer()
                timer_q.put(t)


            file_buf = f.read(PAYLOAD_SIZE)
            seq_num += 1 
            seq_q.put(seq_num)
        
        else:
            #check timer
            t = timer_q.get()
            delta_t = next(t)
            print (delta_t)
            if (delta_t >= TIMEOUT):#if we time out, resend all unacked packets in window
                print("Retransmitting")

                t = timer()
                timer_q.put(t)

                i = base
                f.seek(i*1024)
                
                for i in range(seq_num):
                    file_buf = f.read(PAYLOAD_SIZE)
                    s_buf, end = make_packet(i, file_buf)
                    sock.sendto(s_buf, (HOST, PORT))

    

    print("finished")

    t1.join()    
    f.close()    


    delta = time.time() - start
    tp = round((file_size/delta)/1000)

    output = "{} {}".format(retries, tp) 
    print (output)


if __name__ == "__main__": 
    main(sys.argv)


