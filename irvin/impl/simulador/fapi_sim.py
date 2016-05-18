#!/bin/python2
# -*- coding: cp1252 -*-
import socket
import time
import struct
import random
def conect(local):
    conect_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:

        len_Ven = 0x00
        buff_Length = 4
        sub_frame = 0
        sys_frame_n = 0
        num_of_harq = 0
        rnti = 0
        harq_tb2 = 0

        for sys in range(0,1024):
            sys_frame_n = sys

            for sub in range(0,10):
                if ((random.randint(0,10)) is sub):
                    sub_frame=sub
                    frame = (sub_frame & 0x0F) | (sys_frame_n << 4)

                    msg_Id = 0x85
                    harq_tb1 = random.randint(0,1)

                    mensagem = struct.pack('>BBHHHHBB', msg_Id,len_Ven,buff_Length, frame,num_of_harq, rnti, harq_tb1, harq_tb2)
                    conect_socket.sendto(mensagem, local)
                    time.sleep(0.0001)
                    #print len(mensagem)
                else:
                    msg_Id = 0x82
                    sub_frame=sub
                    frame = (sub_frame & 0x0F) | (sys_frame_n << 4)
                    mensagem = struct.pack('>BBHH', msg_Id,len_Ven,buff_Length, frame)
                    conect_socket.sendto(mensagem, local)
                    time.sleep(0.0001)
#                    print len(mensagem)
def main():
    mensagem=''
    port = 8888
    ip = "10.202.35.138"
    local=((ip, port))

    conect(local)

if __name__ == '__main__':
    main()
