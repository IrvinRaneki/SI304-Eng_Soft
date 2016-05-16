#!/bin/python2
# -*- coding: cp1252 -*-


#impott para window
import Tkinter
from Tkinter import *
import time

#import para plot
import threading
import pylab
from pylab import *
import matplotlib.pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from collections import deque

#impot para leitura
import socket
from struct import *
#import random

###############################globais de media#################################
lista_media = deque([0]*1000)
################################globais de cqi##################################
lista_cqi = deque([0]*1000)
valores_cqi = deque([0]*50)
contador_amostra_cqi = 0
flag_plot_cqi = False
###############################globais de bler##################################
lista_bler = deque([0]*1000)
contador_harq=0
contador_amostra_bler=1
################################################################################
def delete_item():
    global lista_bler, lista_media
    del lista_bler[len(lista_bler)-1]
    del lista_media[len(lista_media)-1]

def delete_cqi():
    global lista_cqi
    for i in range(0,50):
        del lista_cqi[len(lista_cqi)-1]
################################################################################
##
## Criacao da UI principal
##
################################################################################
###############################UI principal#####################################
################################################################################
class Window(Tkinter.Frame):
    """docstring for Window"""
    def __init__(self, parent):
        global parente, blers, cqis

        Tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()
        parente = self.parent

        blers = IntVar()
        bler_chk=Checkbutton(parente, text="On/Off - BLER", variable=blers)
        bler_chk.pack()


        cqis = IntVar()
        cqi_chk=Checkbutton(parente,text="On/Off - CQI Indication",variable=cqis)
        cqi_chk.pack()

    def initUI(self):
        menubar = Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu =  Menu(menubar)
        menubar.add_cascade(label="File", underline=0, menu=fileMenu)
        fileMenu.add_command(label="Plot", underline=0, command=self.init_plot)
        fileMenu.add_command(label="Exit", underline=0, command=self.onExit)
    #################################FUNCOES####################################

    def onExit(self):
        time.sleep(0.5)
        self.th_plot.stop()
        self.th_leitura.stop()
        self.parent.destroy()
        #self.parent.quit()

    def init_plot(self):
        self.th_plot = Trd_plot()
        self.th_plot.start()
        self.th_leitura = Trd_leitura()
        self.th_leitura.start()

################################################################################
##
## Criacao do Plot
##
################################################################################
##############################CLASS_THREAD######################################
################################################################################
class Trd_plot(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.paused = True
        self._running = True
        self.state = threading.Condition()

    def run(self):
        #parente = parent de window
        #lista_bler = deque (lista_bler circular de valores de line)
        global parente, lista_bler, contador_harq, contador_amostra_bler
        global lista_cqi, flag_plot_cqi
        ########################################################################
        #                     Criacao do Grafico e Tollbar                     #
        ########################################################################

        figura = pylab.figure(1)
        ax = figura.add_axes([0.1,0.1,0.8,0.8])
        ax.grid(True)

        ax.set_title("Plot Bler-Azul / Media de Bler-Vermelho / CQI indication - Verde")
        ax.set_xlabel("Time - 0.5 segundos")
        ax.set_ylabel("Amplitude - Bler/Media em porcentagem / CQI valor real")
        ax.axis([0,1000,0,100])

        line_bler, = pylab.plot(lista_bler)
        line_media, = pylab.plot(lista_media, 'r')#lista_bler de media
        line_cqi, = pylab.plot(lista_cqi, 'g')#lista_cqi

        canvas =  FigureCanvasTkAgg(figura, master=parente)
        canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        canvas.show()

        toolbar = NavigationToolbar2TkAgg(canvas, parente)
        toolbar.update()
        canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)
        ########################################################################
        #                         Geracao do grafico                           #
        ########################################################################
        media = 0
        global blers
        while True:
            valor_plot_bler = (contador_harq/contador_amostra_bler)*100
            #print 'Amostras: ', contador_amostra_bler, ' Harq is not 1: ', contador_harq, ' BLER: ', valor_plot_bler
            plot_bler = blers.get()
            if plot_bler is 0:
                valor_plot_bler = 0
            ####################################################################
            soma = 0
            v = 0
            for v in range(0,50):
                soma += lista_bler[v]
            media = (soma)/50
            ####################################################################
            if flag_plot_cqi is True:
                delete_cqi()
                lista_cqi.extendleft(valores_cqi)
                line_cqi.set_ydata(lista_cqi)

                delete_item()
                lista_bler.appendleft(valor_plot_bler)
                lista_media.appendleft(media)

                line_media.set_ydata(lista_media)
                line_bler.set_ydata(lista_bler)

                canvas.draw()
                flag_plot_cqi = False

            else:

                delete_item()
                lista_bler.appendleft(valor_plot_bler)
                lista_media.appendleft(media)

                line_media.set_ydata(lista_media)
                line_bler.set_ydata(lista_bler)

                canvas.draw()

            contador_amostra_bler = 1.0
            contador_harq = 0
            time.sleep(0.05)

    ############################################################################
    def stop(self):
        with self.state:
            self.stop = True
            self._running=False

################################################################################
##
## Leitura socket
##
################################################################################
##############################CLASS_THREAD######################################
################################################################################
class Trd_leitura(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.daemon = True
        self.paused = True
        self.state  = threading.Condition()

    def run(self):
        #globais de bler
        global contador_harq, contador_amostra_bler
        #globais de cqi
        global contador_amostra_cqi, flag_plot_cqi, valores_cqi
        ##########  conexao  ###############################################
        host=''
        port=8888
        local=(host, port)
        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp.bind(local)
        ####################################################################
        while True:
            contador_amostra_cqi = 0
            plot_cqi=cqis.get()
            while contador_amostra_cqi<50:

                leitor, recebe = udp.recvfrom(65535)
                msg_Id,len_Ven,buff_Length,frame=unpack('>BBHH',leitor[0:6])

                ############################################################
                ############ ----configuracoes de bler----- ################
                if msg_Id is 133:
                    contador_amostra_bler +=1
                    try:
                        msg_Id, len_Ven, buff_Length, frame_bler, num_of_harq, rnti, harq_tb1, harq_tb2 = unpack('>BBHHHHBB', leitor)
                        ############################################################
                        ######### ----configuracoes de descompacta----- ############
                        Sfn=int(frame_bler) >> 4
                        Sf=int(frame_bler) & 0xF
                        if (harq_tb1 is not 1):
                            contador_harq+=1

                    except Exception as e:
                        raise

                ############################################################
                ############ ----configuracoes de CQI ----- ################
                if msg_Id is 139:
                    try:
                        frame_cqi, num_of_cqi, handle, rnti, length, data_offset, timming_advance, ul_cqi, ri =unpack('>HHLHHHHBB', leitor[4:22])
                        ############################################################
                        ######### ----configuracoes de descompacta----- ############
                        Sfn=int(frame_cqi) >> 4
                        Sf=int(frame_cqi) & 0xF
                        if plot_cqi is 0:
                            valores_cqi[contador_amostra_cqi]=0
                            contador_amostra_cqi+=1

                        else:
                            valores_cqi[contador_amostra_cqi]=(ul_cqi-128)/2
                            contador_amostra_cqi+=1

                        if (contador_amostra_cqi > 49):
                            flag_plot_cqi = True
                            time.sleep(0.05)
                            #contador_amostra_cqi = 0
                        else:
                            flag_plot_cqi = False

                    except Exception as e:
                        raise

    def stop(self):
        with self.state:
            self.stop = True
            self._running=False
