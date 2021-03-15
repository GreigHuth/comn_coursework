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

    #initialise expected ack
    expected_seq = 0
    while recv: # while there is data in the socket, keep recieving it

        
        r_buf = recv[0]#recieve data into buffer
        sender = recv[1] # sender address 
        r_buf = bytearray(r_buf)#cast data into byte array

        

        seq = int.from_bytes(r_buf[0:2], "big") # sequence number
        eof = r_buf[2] #eof flag
        payload = r_buf[3:] 
        #print(seq)

        if (seq == expected_seq):
            #print("Correct ack received")
            #print(seq)

            ack = seq.to_bytes(2, byteorder='big') # we just send the sequence number back and that will suffice for ack
            sock.sendto(ack, sender) # send ack

            total += len(payload)#update ack tracker

            if (eof == 1):
                print("End of file reached")
                eof = 0 #reset EOF flag, just in case
                print("total bytes recieved: %d"%total)
                f.write(payload)
                f.close()
                break

            
            
            expected_seq += 1 #increment expected sequence number after getting packet
        
            f.write(payload)#write to file
                
            

        else:
            #print("Wrong ack, sending ack for most recent in order packet")
            if expected_seq == 0:
                ack = (0).to_bytes(2, byteorder='big')
            else:
                ack = (expected_seq - 1).to_bytes(2, byteorder='big') #previous in order packet is the packet before the expected one
            
            sock.sendto(ack, sender) # send duplicate ack
        

        #regardless of what happens, recieve next packet
        recv = sock.recvfrom(PACKET_SIZE)


    

if __name__ == "__main__": 
    main(sys.argv)