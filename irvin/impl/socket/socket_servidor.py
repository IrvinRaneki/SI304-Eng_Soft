#########=====servpy=====##########
#!/user/bin/python
import socket
from collections import deque
import matplotlib.pyplot as plt

import time
##################################################################
#                          plota grafico                         #
##################################################################
def plota_graf(addr, num):
    a1 = deque([0]*100)
    ax = plt.axes(xlim=(0,100), ylim=(0,10))
    d = conect(addr, num)

    line, = plt.plot(a1)
    plt.ion()
    plt.ylim([-15,15])
    plt.show()
    while True:
        a1.appendleft(next(d))
        retira_1 = a1.pop()
        line.set_ydata(a1)
        plt.draw()
        plt.pause(0.1)

##################################################################
#             funcao conect: aguarda o recebimento da msg        #
##################################################################
def conect(addr, recebe):
    serv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #->mecanismos de recepcao de conexao - argv[1-familia do protocolo() 2-tipo de envio(tcp/ip)]
    serv_socket.bind(addr)
    #->mostra qual o ip e porta o servidor devem aguardar a conexao
    while True:
        recebe, cliente = serv_socket.recvfrom(1024)
        #->apos conexao ha o aguardo de dado enviado pela rede de ate 1024 Bytes (1 argv -> tamanho do buffer)
        print "mensagem recebida: "+ recebe
        yield recebe
    serv_socket.close()

##################################################################
#                           funcao main                          #
##################################################################
def main():
    recebe=''
    host = ''
    port = 8888
    addr = (host, port)

    plota_graf(addr, recebe)

if __name__ == '__main__':
    main()
