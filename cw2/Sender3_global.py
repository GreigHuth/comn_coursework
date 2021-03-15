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
base = 0
seq_num = 0
end = False
tp = 0
c = threading.Condition()


def timer():
    start = round(time.time() * 1000)
    while True:
        yield round(time.time() * 1000) - start


def make_packet(i, file_buf):

    seq = i.to_bytes(2, byteorder='big')#first 2 bytes for sequence number
    
    end = False

    #set eof flag
    eof = (0).to_bytes(1, byteorder='big')

    if (len(file_buf) < PAYLOAD_SIZE): 
        #print ("sending last packet")
        end = True
        eof = (1).to_bytes(1, byteorder='big')

    #construct packet
    s_buf = bytearray()# need a new buffer for every packet
    s_buf[0:0] = seq
    s_buf[2:2] = eof
    s_buf[3:3] = bytearray(file_buf)


    #return packet and seqeuence number of packet
    return s_buf, end


#idk if this is even a good idea but im cba thinking about it rn
def ack_thread(sock):
    global t
    global base
    global seq_num
    global end

    while True:
        
        r_buf = sock.recvfrom(2)#recv 2 bytes for ack

        ack = r_buf[0]
        ack = int.from_bytes(ack, "big")  

        print("Recieved ack : %d"%ack)

        if (ack == (seq_num-1)):#cumulative ack, 
            c.acquire()
            base = ack+1

            if end == True and base==seq_num:
                c.release() 
                break

            if (base == seq_num):
                t = None
            else:
                t = timer()

            c.release() 

        



def send_thread(sock, f, HOST, PORT, N):

    global t
    global base
    global seq_num
    global tp
    global end

    file_buf = f.read(PAYLOAD_SIZE)

    while (file_buf): #while the file can still be read 

        #print("base: %d"% base)
        #print("seq_num: %d"% seq_num)

        c.acquire()
        if (seq_num < (base+N)):
            #print("sending packet")
            s_buf, end = make_packet(seq_num, file_buf)
            sock.sendto(s_buf, (HOST, PORT)) #send data
            tp += len(file_buf)
            
            if (base == seq_num): #set timer if first packet in window
                t = timer()

            
            seq_num += 1 
            
            #only read the next part of the file if we actually sent the last part
            file_buf = f.read(PAYLOAD_SIZE)

            if end == True:
                c.release()
                break

        c.release()




def main(argv):

    #performance tracking
    retries   = 0   #number of retransmissions

    #unpack arguments
    HOST = argv[1]
    PORT = int(argv[2])
    FILE = argv[3].encode('utf-8')
    TIMEOUT = int(argv[4])
    N = int(argv[5]) #window size

    global t 
    global base
    global seq_num
    global end
    global tp

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    

    f = open(FILE, 'rb')

    #thread for recieving acks
    t1 = threading.Thread(target=ack_thread, args=(sock,))
    t1.start()
    
    t2 = threading.Thread(target=send_thread, args=(sock, f, HOST, PORT, N)) 
    t2.start()
    start = time.time()#performance measuring

    time.sleep(0.1)#wait for threads to init
    while True:

        try:
            delta_t = next(t)
        except TypeError:
            continue

        c.acquire()
        if (delta_t >= TIMEOUT):#if we time out, resend all unacked packets in window
            #print("retransmitting")
            t = timer()
            
            
            i = base
            f.seek(i*PAYLOAD_SIZE)
                
            for i in range(i, seq_num):
                retries += 1
                file_buf = f.read(PAYLOAD_SIZE)
                s_buf, end = make_packet(i, file_buf)
                sock.sendto(s_buf, (HOST, PORT))

            #f.seek(seq_num*PAYLOAD_SIZE)
            file_buf = f.read(PAYLOAD_SIZE)

            
        if end == True and base==seq_num:
            #if we have sent the last packet and its been acked then we can break
            c.release()
            break
        c.release()

    print("Finished")
    #end
    t1.join()    
    t2.join()
    f.close()    


    delta = time.time() - start
    print("tp: %d"%tp)
    print("delta: %d"%delta)
    print()
    tp = (tp/delta)/1000
    output = "{} {}".format(retries, tp) 
    print (output)


if __name__ == "__main__": 
    main(sys.argv)


