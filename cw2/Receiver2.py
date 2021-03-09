import socket
import sys
import select
import time

PACKET_SIZE = 1027


def main(argv):

    PORT = int (argv[1])
    FILE = argv[2]

    total = 0
    eof = 0 #inititalise EOF so it doesnt accidentally trigger for some reason

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))#bind to all interfaces


    #open file for writing to
    f = open(FILE, 'wb+')
    recv = sock.recvfrom(PACKET_SIZE)

    prev_ack = None
    while recv: # while there is data in the socket, keep recieving it

        
        r_buf = recv[0]#recieve data into buffer
        sender = recv[1] # sender address 
        r_buf = bytearray(r_buf)#cast data into byte array

        

        seq = r_buf[0:2] # sequence number
        eof = r_buf[2] 
        payload = r_buf[3:] 

        ack = seq # we just send the sequence number back and that will suffice for ack
        sock.sendto(ack, sender) # send ack, we dont need to wait for a repsonse

        if ack != prev_ack: #duplicate packet, ignore

            if eof == 1:
                print("End of file reached")
                eof = 0 #reset EOF flag, just in case
                print("total bytes recieved: %d"%total)
                f.write(payload)
                f.close()
                break

            total += len(payload)
            #update ack tracker
            prev_ack = ack
            #write to file
            f.write(payload)
            
        #recieve next payload
        recv = sock.recvfrom(PACKET_SIZE)


    

if __name__ == "__main__": 
    main(sys.argv)