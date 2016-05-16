#!/bin/python2
# -*- coding: cp1252 -*-

import pylab
from pylab import *
import Tkinter
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

import matplotlib.pyplot as plt
import time
from collections import deque
import random

from struct import *
import socket

import threading
################################################################################
################################################################################
################################################################################
x_linha=3000                    ##escala de x(tanto no deque quanto no grafico)
flag=False                      ##flag que avisa quando completa o buffer
valor_plot_bler = 0             ##valor inicial para bler
valor_plot_cqi = range(0,25)    ##buffer inicial para cqi

lista_bler=deque([0]*x_linha)   ##lista circular de bler
lista_cqi =deque([0]*x_linha)   ##lista circular de cqi

flag_stop=False
flag_leitura = False
flag_plot_bler=False
flag_plot_cqi =False

cont_harq=1
conta_amostras=1.0
################################################################################
def delete_bler():
  global lista_bler, x_linha
  del lista_bler[len(lista_bler)-1]

def delete_cqi():
  global lista_cqi
  for i in range(0,25):
      del lista_cqi[len(lista_cqi)-1]
################################################################################
################################################################################

################################################################################
#                           Criacao da Classe                                  #
################################################################################
class Packing(Tkinter.Frame):
    """docstring for Packing"""

    def __init__(self, parent):

        Tkinter.Frame.__init__(self, parent)
        self.parent = parent

        self.initUI()
        self.initUI2()
################################################################################
################################################################################

################################################################################
#                               Criacao da UI                                  #
################################################################################
    def initUI(self):

        menubar=Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu=Menu(menubar)
        helpMenu=Menu(menubar)

        ########################################################################
        menubar.add_cascade(label="File",underline=0, menu=fileMenu)

        fileMenu.add_command(label="Plotar", underline=0, command=self.thread_init)
        fileMenu.add_separator()

        fileMenu.add_command(label="Exit", underline=0, command=self.onExit)
        ########################################################################
        submenu=Menu(fileMenu)
        helpMenu.add_command(label="About Program of Plot", underline=0, command=self.about)
        menubar.add_cascade(label="Help",underline=0, menu=helpMenu)
################################################################################
    #Criacao da UI2
    def initUI2(self):
        frame=Frame(self.parent)
        frame.pack(side=LEFT)

        self.b1=Button(frame, text='Encontrar UE',width=10)
        self.b2=Button(frame, text='Plotar CQI ',width=10, command=lambda:self.thread_init(2))
        self.b3=Button(frame, text='Plotar Bler',width=10, command=lambda:self.thread_init(1))
        self.b4=Button(frame, text='Exit',width=10, command=self.onExit)

        #self.b1.pack()
        self.b2.pack()
        self.b3.pack()
        self.b4.pack()
################################################################################
    #funcoes para os botoes
    def thread_init(self, tipo_de_plot):
        global flag_plot_bler, flag_leitura, flag_plot_cqi
        if flag_leitura == False:
            self.th_leitura_bler=threading.Thread(target= self.leitura)
            self.th_leitura_bler.start()
            flag_leitura = True
        else:
            pass

        if ((tipo_de_plot is 1)&(flag_plot_bler is False)):
            self.th_cria_graf_bler = threading.Thread(target = self.cria_grafi_bler)
            self.th_cria_graf_bler.start()
            flag_plot_bler = True

        if ((tipo_de_plot is 2)&(flag_plot_cqi is False)):
            self.th_cria_graf_cqi = threading.Thread(target = self.cria_grafi_cqi)
            self.th_cria_graf_cqi.start()
            flag_plot_cqi = True

    def onExit(self):
        global flag_stop
        flag_stop = True
        time.sleep(1)
        self.parent.destroy()
        self.parent.quit()

    def about(self):
        top = Toplevel()
        top.geometry("400x300")
        top.title("About")

        msg_about=Label(top, text="\nEste programa foi idealizado pela equipe de\n"
                        "Software da Gerencia de Redes sem Fio do CPqD\n"
                        "(Centro de Pesquisa e Desenvolvimento em Telecom)\n"
                        "com o intuito de auxiliar e examinar os sinais\n"
                        "e mensagens entre UE e eNodeB",width=50).pack()
        msg_devol=Label(top, text="\nDesenvolvedor: Irvin R. Gomes").pack()

    ########################################################################
    ########################################################################

    ########################################################################
    #		             conecta e manda para plota                        #
    ########################################################################
    def leitura(self):
        global lista_bler, lista_cqi, flag_stop, conta_amostras, cont_harq, valor_plot_cqi
        ##########  conexao  ###############################################
        host=''
        port=8888
        local=(host, port)
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(local)
        ####################################################################
        ######### ----- configuracoes de leitura  ----- ##########
        contador_cqi = 0
        while flag_stop == False:
            leitor, recebe = udp.recvfrom(65535)
            msg_Id,len_Ven,buff_Length, Frame=unpack('>BBHH', leitor[0:6])
            ############################################################
            ######### ----configuracoes de descompacta----- ############
            Sfn=int(Frame) >> 4
            Sf=int(Frame) & 0xF

            if msg_Id is 133 & flag_plot_bler is True:
                conta_amostras +=1
                try:
                    msg_Id,len_Ven,buff_Length,Frame, num_of_harq, rnti, harq_tb1, harq_tb2 = unpack('>BBHHHHBB', leitor)
                    if (harq_tb1 is not 1):
                        cont_harq +=1
                except Exception as e:
                #    print ":".join("{:02x}".format(ord(c)) for c in leitor)
                    raise

            if msg_Id is 139 & flag_plot_cqi is True:
                try:
                    sub_Frame,num_of_cqi, handle, rnti, length, data_offset, timming_advance, ul_cqi, ri =unpack('>HHLHHHHBB', leitor[4:22])

                    valor_plot_cqi[contador_cqi]=(ul_cqi-128)/2
                    contador_cqi += 1
                    if contador_cqi is 24:
                        flag_plot_cqi = True
                        contador_cqi = 0
                    else:
                        flag_plot_cqi=False
                except Exception as e:
                    raise
################################################################################
################################################################################

################################################################################
#                           Criacao  do grafico                                #
################################################################################
    def cria_grafi_bler(self):
        global valor_plot_cqi, lista_bler, flag, flag_stop, cont_harq, conta_amostras
        ########################################################################
        #                     Criacao do Grafico e Tollbar                     #
        ########################################################################
        fig = pylab.figure(1)
        ax = fig.add_axes([0.1,0.1,0.8,0.8])
        ax.grid(True)
        ax.set_title("RealTime plot FAPI - BLER INDICATION")
        ax.set_xlabel("Tempo (em 0,05 segundos)")
        ax.set_ylabel("Amplitude(em porcentagem)")
        ax.axis([0,1200,0,100])


        line, = pylab.plot(lista_bler)

        canvas = FigureCanvasTkAgg(fig, master=self.parent)
        canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        canvas.show()

        toolbar = NavigationToolbar2TkAgg( canvas, self.parent )
        toolbar.update()
        canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

        ########################################################################
        #                         Geracao do grafico                           #
        ########################################################################
        while flag_stop == False:

            valor_plot_bler = (cont_harq/conta_amostras)*100

            delete_bler()
            lista_bler.appendleft(valor_plot_bler)
            line.set_ydata(lista_bler)

            canvas.draw()
            conta_amostras = 1.0
            cont_harq = 0
            time.sleep(0.05)

################################################################################
################################################################################
    def cria_grafi_cqi(self):
        global lista_cqi, flag_plot_cqi, flag_stop, x_linha
        fig2 = pylab.figure(2)
        ax2 = fig2.add_axes([0.1,0.1,0.8,0.8])
        ax2.grid(True)
        ax2.set_title("RealTime plot FAPI - CQI INDICATION")
        ax2.set_xlabel("Time")
        ax2.set_ylabel("Amplitude")
        ax2.axis([0,1000,0,100])
        line2, = pylab.plot(lista_cqi)

        canvas2 = FigureCanvasTkAgg(fig2, master=self.parent)
        canvas2.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        canvas2.show()
        toolbar2 = NavigationToolbar2TkAgg( canvas2, self.parent)
        toolbar2.update()
        canvas2._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        ########################################################################
        #                         Geracao do grafico                           #
        ########################################################################
        while flag_stop == False:

            delete_cqi()
            lista_cqi.extendleft(valor_plot_cqi)
            line2.set_ydata(lista_cqi)
            canvas2.draw()
################################################################################
#                                    Main                                      #
################################################################################
def main():

    root=Tkinter.Tk()
    root.wm_title("FAPI Log Analyzer")
    app=Packing(root)
    root.geometry("700x600")
    root.mainloop()

if __name__ == '__main__':
    main()
