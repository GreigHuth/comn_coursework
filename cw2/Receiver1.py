import socket
import sys
import select

PACKET_SIZE = 1027



def main(argv):

    PORT = int (argv[1])
    FILE = argv[2]

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", PORT))#bind to all interfaces


    #open file for writing to
    f = open(FILE, 'wb+')
    recv = sock.recvfrom(PACKET_SIZE)

    while recv: # while there is data in the socket, keep recieving it

        
        r_buf = recv[0]#recieve data into buffer
        r_buf = bytearray(r_buf)#cast data into byte array

        seq = r_buf[0:2] # sequence number
        eof = r_buf[2] 
        payload = r_buf[3:] 

        seq = int.from_bytes(seq, byteorder="big")

        if eof == 1:
            print("End of file reached")
            f.write(payload)
            f.close()
            break

        f.write(payload)

        #recieve next payload
        recv = sock.recvfrom(PACKET_SIZE)


if __name__ == "__main__": 
    main(sys.argv)