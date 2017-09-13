#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.uic import *
# import ConfigParser
import PLOTEOTR

import pyqtgraph as pg

import time, string, csv, serial, sys, random  # , resource
import numpy as np
from collections import deque  # double ended queue

"""########################################################## CLASE PARA IU"""


class Myform(QtGui.QMainWindow):
    def __init__(self, parent=None):
        locale = unicode(QtCore.QLocale.system().name())
        QtGui.QWidget.__init__(self, parent)
        self.ui = loadUi("CicladorIG.ui", self)

        # self.win = self.ui.plot.GraphicsWindow(title="Ventana de graficado")
        # self.ui.plot.setConfigOptions(antialias=True)

        self.Ploteo1 = self.ui.plot.addPlot(row=0, col=0)
        self.Ploteo2 = self.ui.plot.addPlot(row=1, col=0)

        self.threadPool = []
        global CondSeteo
        global CondGuardado
        CondGuardado = [['a', False, 0.0], ['b', False, 0.0],
                        ['c', False, 0.0], ['d', False, 0.0],
                        ['e', False, 0.0], ['f', False, 0.0],
                        ['g', False, 0.0], ['h', False, 0.0],
                        ['i', False, 0.0], ['j', False, 0.0],
                        ['k', False, 0.0], ['l', False, 0.0],
                        ['m', False, 0.0], ['n', False, 0.0],
                        ['o', False, 0.0], ['p', False, 0.0]]
        #            [celda, Activa?, Promediado]
        CondSeteo = [['a', 0, 0, 0, 0, 0], ['b', 0, 0, 0, 0, 0],
                     ['c', 0, 0, 0, 0, 0], ['d', 0, 0, 0, 0, 0],
                     ['e', 0, 0, 0, 0, 0], ['f', 0, 0, 0, 0, 0],
                     ['g', 0, 0, 0, 0, 0], ['h', 0, 0, 0, 0, 0],
                     ['i', 0, 0, 0, 0, 0], ['j', 0, 0, 0, 0, 0],
                     ['k', 0, 0, 0, 0, 0], ['l', 0, 0, 0, 0, 0],
                     ['m', 0, 0, 0, 0, 0], ['n', 0, 0, 0, 0, 0],
                     ['o', 0, 0, 0, 0, 0], ['p', 0, 0, 0, 0, 0]]
        # [celda, barr, vli, vls, tmax, corr]

        self.filaPloteo = deque(maxlen=16000)

        self.ui.BotActivo.setCheckable(True)
        self.ui.BotSetearC.setCheckable(True)
        self.ui.BotSetearV.setCheckable(True)
        self.ui.BotParaPlot.setCheckable(True)

    def inicioVOC(self):

        Celda = self.ui.cmbCelV.currentText()
        Promedio = float(self.ui.cmbPromV.currentText())
        Corriente = 0
        Ciclos = 1
        V_lim_inf = -99999
        V_lim_sup = 99999
        T_Max = int(self.ui.LinEdTiemV.text())
        self.inicio(Celda, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max)

    def inicioCiclado(self):

        # seteo valores para el proceso
        Celda = self.ui.cmbCelC.currentText()
        Promedio = float(self.ui.cmbProm.currentText())
        Corriente = int(self.ui.LinEdCorri.text())
        Ciclos = int(self.ui.LinEdCiclos.text()) * 2
        V_lim_inf = int(self.ui.LinEdVLInf.text())  # funcion que convierta de acuerdo a lectura!
        V_lim_sup = int(self.ui.LinEdVLSup.text())
        T_Max = int(self.ui.LinEdTMax.text()	)
        self.inicio(Celda ,Promedio ,Corriente ,Ciclos ,V_lim_inf ,V_lim_sup ,T_Max)

    def inicio(self, Celda, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max):
        global FIN
        global ser
        global PorSetear
        FIN=False
        PorSetear=None
        # modifico valores de condiciones de seteo solo si la celda no esta en proceso
        if self.CeldaLibre(Celda) :
            self.ActualizoCondGuardado(Celda,False, float( Promedio))
            ActualizoMatriz(Celda,Ciclos, V_lim_sup,V_lim_inf ,T_Max, Corriente )
            if self.ui.BotActivo.isChecked():
                PorSetear=Celda
                self.ui.BotSetearV.setChecked(False)
                self.ui.BotSetearC.setChecked(False)
            else :
                # ENVIO
                EnviarPS_I(Corriente,False,str (Celda ))
                self.chequeaRB(Celda,True)
                fila=deque( maxlen=16000)  ################################## definirlo aca implica que es el incicio
                self.ui.BotSetearV.setChecked(False)
                self.ui.BotSetearC.setChecked(False)
                self.ui.BotActivo.setChecked(True)
                # inicio lectura
                self.threadPool.append( LECTURA(fila,self. filaPloteo) )

                # self.disconnect(self.threadPool[len(self.threadPool)-1], self.threadPool[len(self.threadPool)-1].signal, self.ActualValores) ############
                self.connect(self.threadPool[len(self.threadPool)-1], self .
                             threadPool[len(self.threadPool)-1]. signal , self.ActualValores)

                self.threadPool[len(self.threadPool)-1].start ( )
                time.sleep(0.5)
                # inicio procesamiento
                self.threadPool.append( PROCESO(fila) )
                self.threadPool[len(self.threadPool)-1]. start ()
        else :
            print 'imposible setear celda no libre'

        if PorSetear!=None:
            self.chequeaRB(PorSetear,True)

    def chequeaRB(self, celda, estado):
        if celda == 'a':
            self.ui.RBa.setChecked(estado)
        elif celda == 'b':
            self.ui.RBb.setChecked(estado)
        elif celda == 'c':
            self.ui.RBc.setChecked(estado)
        elif celda == 'd':
            self.ui.RBd.setChecked(estado)
        elif celda == 'e':
            self.ui.RBe.setChecked(estado)
        elif celda == 'f':
            self.ui.RBf.setChecked(estado)
        elif celda == 'g':
            self.ui.RBg.setChecked(estado)
        elif celda == 'h':
            self.ui.RBh.setChecked(estado)
        elif celda == 'i':
            self.ui.RBi.setChecked(estado)
        elif celda == 'j':
            self.ui.RBj.setChecked(estado)
        elif celda == 'k':
            self.ui.RBk.setChecked(estado)
        elif celda == 'l':
            self.ui.RBl.setChecked(estado)
        elif celda == 'm':
            self.ui.RBm.setChecked(estado)
        elif celda == 'n':
            self.ui.RBn.setChecked(estado)
        elif celda == 'o':
            self.ui.RBo.setChecked(estado)
        elif celda == 'p':
            self.ui.RBp.setChecked(estado)

    def ActualizoCondGuardado(self,Celda, Activa, Promedio ):
        global CondGuardado
        # print 'desde actualizo guardado la celda ' + str(Celda) + 'esta activa? ' + str(Activa)
        # self.chequeaRB(Celda, Activa)
        # print 'Actualizo  Guardado ' + str(Celda) + str(Activa)
        for i in range(len(string.ascii_letters)):
            if Celda == string.ascii_letters[i]:
                CondGuardado[i][1]=Activa
                CondGuardado[i][2]= Promedio
                break

    def PararCelda(self):  # adicionar mandar i=0 para cuando para celda usar por setear en 0
        global PorSetear
        # global CondSeteo
        Celda=self.ui . cmbCelPlot.currentText()
        print '\n\nfinalizada celda: '+str( Celda)+ ' por usuario\n\n'
        # self.ActualizoCondGuardado(Celda,False,0.0)
        ActualizoMatriz(Celda,0,0,0,1,0)  # barridos 0 y corriente 0 y tiempoMax mayor a cero pero minimo
        PorSetear=Celda # para finalizar hago barridos de seteo como 0 (el resto me da lo mismo?)
        # luego la lectura me reinicia cond de seteo y pa barrer
        # eso me hace cerrar el archivo
        # y en proceso me actuliza cond de guardado a ['cel',False, 0]


    def ActCondUi(self):
        global CondSeteo
        global CondGuardado
        Celda=self.ui.cmbCelC. currentText()
        reng=NumDeCelda(Celda)
        self.ui.LinEdCorri.setText(str(CondSeteo[reng][5]))
        self.ui.LinEdCiclos.setText(str(CondSeteo[reng][1]))
        self.ui.LinEdVLInf.setText(str(CondSeteo[reng][3]))
        self.ui.LinEdVLSup.setText(str(CondSeteo[reng][2]))
        self.ui.LinEdTMax.setText(str(CondSeteo[reng][4]))
        if CondGuardado[reng][2] == 100:
            self.ui.cmbProm.setCurrentIndex(7) ###promediado  elif CondGuardado[reng][2] == 50:
            self.ui.cmbProm.setCurrentIndex(6)
        elif CondGuardado[reng][2] == 25:
            self.ui.cmbProm.setCurrentIndex(5)
        elif CondGuardado[reng][2] == 10:
            self.ui.cmbProm.setCurrentIndex(4)
        elif CondGuardado[reng][2] == 5:
            self.ui.cmbProm.setCurrentIndex(3)
        elif CondGuardado[reng][2] == 1:
            self.ui.cmbProm.setCurrentIndex(2)
        elif CondGuardado[reng][2] == 0.5:
            self.ui.cmbProm.setCurrentIndex(1)
        else:
            self.ui.cmbProm.setCurrentIndex(0)

    def Reseteo(self):
        # Voc
        self.ui.cmbCelV.setCurrentIndex(0)
        self.ui.LinEdTiemV.setText('10')
        self.ui.cmbPromV.setCurrentIndex(5)
        # Ciclado
        self.ui.cmbCelC.setCurrentIndex(0)
        self.ui.LinEdCorri.setText('1000')
        self.ui.LinEdCiclos.setText('10')
        self.ui.LinEdVLInf.setText('-999999')
        self.ui.LinEdVLSup.setText('999999')
        self.ui.LinEdTMax.setText('12')
        self.ui.cmbProm.setCurrentIndex(7)

    def ActualValores(self, barrido, Vin, Iin, Tiem):
        self.ui.SalBarrido.setText(str(barrido))
        self.ui.SalVInst.setText(str(Vin))
        self.ui.SalIInst.setText(str(Iin))
        self.ui.SalTiemp.setText(str(Tiem))

    """ ############################################################## PLOTEO """
    def LimPant(self):
        self.Ploteo1.clear()
        self.Ploteo2.clear()

    def Plot(self):
        Celda=self.ui.cmbCelPlot. currentText()
        if self.ui.RBTiemReal.isChecked():
            ploteo1 = self.Ploteo1.plot()
            ploteo2 = self.Ploteo2.plot()

            self.threadPool.append( PLOTEOTR(Celda,self.filaPloteo) )

            self.threadPool[len(self.threadPool)-1].newData1.connect(self. update1)
            self.threadPool[len(self.threadPool)-1].newData2.connect(self. update2)

            self.threadPool[len(self.threadPool)-1].start()

        elif self .ui.RBPlotFin.isChecked():
            listaBarr = str(self.ui.LELisBarridos.text())
            listaBarr=listaBarr.split(',')
            self.PlotFinal(str(Celda),listaBarr)

        elif self .ui.RDdefinido.isChecked():
            Inicial=int(self.ui.LEBarIn.text())
            Final=int(self.ui.LEBarFin.text())
            self.PlotEntreVal(Inicial,Final,Celda)

        elif self.ui. RBCapac.isChecked():
            PesoAnodo=float(self.ui.LEPesoAnodo. text ())
            self.PlotFinalCapacidades(Celda,PesoAnodo)

    def update1( self, data1):
        self.Ploteo1.plot(data1,pen='g',clear=True)  # data2,clear=True)
        self.Ploteo1.setLabel('left', text='Tension', units='mV', unitPrefix=None)
        self.Ploteo1. showGrid(x=True, y=True, alpha=None)
        # setLabel(axis, text=None, units=None, unitPrefix=None, **args)
    def update2(self, data2):
        self.Ploteo2.plot(data2, pen='r', clear=True)
        self.Ploteo2.setLabel('left', text='Corriente', units='uA',unitPrefix=None)
        self.Ploteo2.showGrid(x=True, y=True, alpha=None)

    def PlotFinal(self,Celda,barridos):
        DequePLOT = deque()
        nombre ='Arch_Cn-'+ str(Celda) +'.csv'
        with open(nombre) as f:
            reader = csv.reader(f, delimiter="\t")
            next(f)
            for line in reader:
                linea = line[0].split(',', 3)
                renglon=[]
                for elemento in linea:
                    if elemento == ' ----- ':
                        break
                    else:
                        renglon+=float(elemento), DequePLOT.append( renglon)
        ValT=[]
        ValX=[]

        self.Ploteo1.clear()
        self.Ploteo2.clear()
        for j in barridos:
            j=int(j)
            print str(len(DequePLOT))
            for i in range(len(DequePLOT)-2):
                if DequePLOT[i][0] >= j:
                    if DequePLOT[i][3]==0 and len(ValT)!=0 :
                        self.Ploteo1.plot(ValT, ValX , pen=(j,len(barridos)))
                        print 'carga ' + str(len(ValT))
                        ValT=[]
                        ValX=[]
                        ValT+=DequePLOT [i][3],
                        ValX+=DequePLOT[i][1],  # tension
                    else :
                        ValT+=DequePLOT[i][3] ,
                        ValX+=DequePLOT[i][1],  # tension
                if DequePLOT[i][0]>j:
                    print 'descarga ' + str(len(ValT))
                    self.Ploteo1.plot(ValT, ValX, pen=(j,len(barridos)))
                    ValT=[]
                    ValX=[]
                    break
            self.Ploteo1.setLabel('left', text= 'Tension', units='mV', unitPrefix=None)
            self.Ploteo1.showGrid(x=True, y=True, alpha=None)


        DequePLOT.clear()

    def PlotFinalCapacidades(self, Celda, PesoAnodo):
        DequePLOT = deque()
        nombre ='Arch_Cn-'+ str(Celda) +'.csv'
        with open(nombre) as f:
            reader = csv.reader(f, delimiter ="\t")
            next( f)
            for line in reader:
                linea = line[0].split(',', 3)
                renglon=[]
                for elemento in linea:
                    if elemento == ' ----- ':
                        break
                    else:
                        renglon+=float(elemento),
                DequePLOT.append(renglon)

        barridoMax=DequePLOT[len(DequePLOT)-2 ][ 0]
        print 'barrido ultimo: '+str(barridoMax)

        ValCapacidades=[]
        for i in range(1 , int(barridoMax)+1):
            corriente=tiempo=0.0
            samples=0
            for j in range(len(DequePLOT)-1):
                if DequePLOT[j][0] ==i:
                    samples+=1
                    corriente+=DequePLOT[ j ][2]
                    if DequePLOT[j][3] > tiempo:
                        tiempo = DequePLOT[j][3]
            ValCapacidades+=( corriente/(samples))*(tiempo/ PesoAnodo),
        print ValCapacidades
        # symbol='o',
        self.Ploteo2.clear()
        self. Ploteo2.plot(ValCapacidades, symbol='+', pen= 'r') # self.Ploteo2. setLabel('left' , text='Capacidad Anodica', units='[uA*s/gr]',unitPrefix=None)
        self.Ploteo2.showGrid(x=True, y=True, alpha=None)  # lr2 = pg.LinearRegionItem([0,100])
        # lr2.setZValue(-10)
        # self.Ploteo2.addItem(lr2) #################################################################ver
        # self.Ploteo1.plot(ValX, pen='r')
        # def updatePlot():
        # self.Ploteo1.setXRange(*lr2.getRegion(), padding=0)
        # def updateRegion():
        # lr2.setRegion(self.Ploteo1.getViewBox().viewRange()[0])
        # lr2.sigRegionChanged.connect(updatePlot)
        # self.Ploteo1.sigXRangeChanged.connect(updateRegion)
        # updatePlot()

    def PlotEntreVal(self,Inicial,Final,Celda):
        DequePLOT = deque()
        nombre ='Arch_Cn-'+ str(Celda) +'.csv'
        with open(nombre) as f:
            reader = csv.reader(f, delimiter="\t")
            next(f)
            for line in reader:
                linea = line[0].split(',', 3)
                renglon =[]
                for elemento in linea:
                    if elemento == ' ----- ':
                        break
                    else:
                        renglon+=float(elemento),
                DequePLOT. append(renglon)
        ValT=[]
        ValX=[]
        ValY=[]
        for i in range(len(DequePLOT)-2):  # le cambie el comienzo
            if DequePLOT[i][0] >= Inicial:
                ValT+=DequePLOT[i][3],
                ValX+=DequePLOT[i][1],  # tension
                ValY+= DequePLOT[i][2],  # corriente
            if DequePLOT[i  ][0]>Final:
                break
        DequePLOT.clear()

        self.Ploteo1. clear( )
        self.Ploteo2.clear()
        self.Ploteo2.plot(ValX,  pen='r') #
        self.Ploteo2. plot(ValY, pen='g') #
        self.Ploteo2.setLabel('left', text='Corriente', units='uA',unitPrefix=None)
        self.Ploteo2.showGrid(x=True, y=True, alpha=None)

        lr2 = pg.LinearRegionItem([0,100])
        lr2  .setZValue(-10)
        self.Ploteo2.  addItem(lr2)

        self.Ploteo1.plot(ValX, pen='r')
        def updatePlot():
            self.Ploteo1.setXRange(*lr2.getRegion(), padding=0)
        def updateRegion():
            lr2.setRegion(self.Ploteo1.getViewBox().viewRange()[0])
        lr2.sigRegionChanged.connect(updatePlot)
        self.Ploteo1.sigXRangeChanged.connect(updateRegion)
        updatePlot()

        """############################################################## FUNCIONES Dependientes"""

    def CorrienteDeCelda(self,celda):
        for i in range(len(string.ascii_letters)):
            if celda == string.ascii_letters[i]:
                return MATRIZ[i][6]



    def CeldaLibre(self, celda):
        global CondSeteo
        for i in range(len( string.ascii_letters)):
            if celda == string.ascii_letters[i]:
                if CondSeteo[i][4] != 0:
                    return False
                    break
                else:
                    return True
                    break


def ActualizoMatriz(celda, barridos, VLS, VLI, TMax,  Corriente):
    global CondSeteo
    for i in range(len(string.ascii_letters)):
        if celda == string.ascii_letters[i]:
            CondSeteo[i][1]=barridos
            CondSeteo[i][2]=VLS
            CondSeteo[i][3]=VLI
            CondSeteo[i][4]=TMax
            CondSeteo[i][5]=Corriente
            break

def NumDeCelda(celda):
    for i in range(len(string.ascii_letters)):
        if celda == string. ascii_letters[i]:
            return i
            break

def EnviarPS_I(ua , Descarga, celda):
    print str ( celda)
    ser.write(str(celda))
    # I=0 con uA=0 en cualquier descarga
    # 2 unidades = 1uA 2048 =0A
    # global ser
    # print ser


# print 'ua: ' + str(ua) +' ' +str(type(ua)) + 'Descarga: ' + str(Descarga) +' '  + str(type(Descarga)) +'Celda: '  + str(celda) +' ' + str(type(celda))

    # MatConv=[['h',2],['f',2],['d',2],['b',2],['h',1],['f',1],['d',1],['b',1],['e',2],['g',2],['a',2],['c',2],['e',1],['g',1],['a',1],['c',1]]
    # cada renglon es el orden en asccii, dentro la primer columna es el caracter dentro del dac cuyo numero es la otra

    # letra a enviar MatConv[NumDeCelda(str(celda))][0]
    # numero a enviar MatConv[NumDeCelda(str(celda))][1]

    # if Descarga :
    # num=int(2048-(ua*2))
    # else :
    # num=int((ua*2)+2048)
    # num = ua

    # print 'numero a enviar__: ' +str(num)
    # if num>=0 and num<=4095:
    # mil=num/1000
    # cien=(num-mil*1000)/100
    # die=(num-mil*1000-cien*100)/10
    # un=(num-mil*1000-cien*100-die*10)
    ##print(str(mil)+' '+str(cien)+' '+str(die)+' '+str(un))
    ##inicio
    # ser.write('i')
    ##time.sleep(0.25)
    # ser.write(str(mil)) #1
    ##time.sleep(0.25)
    # ser.write(str(cien)) #2
    ##time.sleep(0.25)
    # ser.write(str(die)) #3
    ##time.sleep(0.25)
    # ser.write(str(un)) #4
    ##time.sleep(0.25)
    # ser.write(str(MatConv[NumDeCelda(str(celda))][0]))
    ##time.sleep(0.25)
    # ser.write(str(MatConv[NumDeCelda(str(celda))][1]))
    ##time.sleep(0.25)
    # ser.write('f')
    ##time.sleep(0.25)
    # ser.flushInput()
    # else:
    # print 'numero incorrecto'

def SeteoPuerto():
    # class serial.Serial
    #  __init__(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE,
    #             stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False,


#             writeTimeout=None, dsrdtr=False, interCharTimeout=None)
    ser = serial.Serial()
    ser.baudrate = 115200
    ser.port = '/dev/ttyACM0'  # '/dev/ttyUSB0' #
    ser.bytesize = 8
    ser.stopbits = 1
    # ser.timeout=0.1     #timeout = x: set timeout to x seconds (float allowed)
    ser.parity = 'N'  # paridad	(E)Par / (O)impar / (N)inguna
    print "el puerto se configura "+ str(ser)  ##################################################################################################################################################################
    ser.open() ###hacer chequeo de que se pueda abrir correctamente
    ##################################################################################################################################################################
    return ser

def  RecibirPS():
    global ser
    s=ser.readline()
    # s=random.random()
    print 'Limpio: "' + str(s) +'"'+ "len es: "+str(len(s))
    # print 's-1' + s[len(s)-1]
    # print 'Cortado: "' + s +'"'
    if len(s) == 13 :
        s=s[:len(s)-1]
        return s
    else:
        return '$#$#$'



