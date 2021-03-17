#Greig Huth 
#s1532620

import socket
import sys
from time import sleep

PAYLOAD_SIZE = 1024
HEADER_SIZE = 3

def main(argv):

    #unpack arguments
    HOST = argv[1]
    PORT = int(argv[2])
    FILE = argv[3].encode('utf-8')

    #set up socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    f = open(FILE, 'rb')
    read_buf = f.read(PAYLOAD_SIZE)
    i = 0
    while (read_buf):

        seq = i.to_bytes(2, byteorder='big')#first 2 bytes for sequence number
        eof = (0).to_bytes(1, byteorder='big')#3rd byte for EOF


        if (len(read_buf) < PAYLOAD_SIZE):
            print("End of file reached")
            eof = (1).to_bytes(1, byteorder='big')

        #print(bytearray(f.read(1024)))

        buffer = bytearray()
        buffer[0:0] = seq
        buffer[2:2] = eof
        buffer[3:3] =  bytearray(read_buf)
        sock.sendto(buffer, (HOST, PORT))

        print(len(buffer))

        #remember to update read buffer and sequence number
        read_buf = f.read(PAYLOAD_SIZE)
        i+=1 



    f.close()    

        



    

if __name__ == "__main__": 
    main(sys.argv)


