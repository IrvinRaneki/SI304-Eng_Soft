#!/bin/python2
# -*- coding: cp1252 -*-
    #codigo para uso de caracteres especiais
from Tkinter import *
import tkMessageBox

################################################################################
#criacao da classe

class Packing(Frame):

    def __init__(self,parent):
        Frame.__init__(self,parent)

        self.parent = parent
        self.initUI()
        self.initUI2()

################################################################################
#criacao da UI

    def initUI(self):
        self.parent.title("Program of Plot")

################################################################################
#Menubar
        menubar=Menu(self.parent)
        self.parent.config(menu=menubar)

        fileMenu=Menu(menubar)
        helpMenu=Menu(menubar)

        fileMenu.add_command(label="Exit", underline=0, command=self.onExit)
        menubar.add_cascade(label="File",underline=0, menu=fileMenu)

        helpMenu.add_command(label="About Program of Plot", underline=0, command=self.about)
        menubar.add_cascade(label="Help",underline=0, menu=helpMenu)

################################################################################
#cricacao de outra layer
    def initUI2(self):
        frame=Frame(self.parent)
        frame.pack(side=TOP)

        self.b4=Button(frame, text='Exit',width=10, command=self.onExit)
        self.b4.pack()
################################################################################
#criacao de funcoes

    def about(self):
        tkMessageBox.showinfo("About","Ainda nao tem nada sobre!!")

    def onExit(self):
        self.quit()

################################################################################
#main

def main():
    raiz=Tk()
    raiz.geometry("300x300")
    app=Packing(raiz)
    raiz.mainloop()


if __name__ == '__main__':
    main()
