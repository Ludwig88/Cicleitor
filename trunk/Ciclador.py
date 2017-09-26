#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui, Qt
from PyQt4.uic import *
# import ConfigParser
import PLOTEOTR

import pyqtgraph as pg

import time, string, csv, sys  # , resource
from collections import deque  # double ended queue

from DatosIndependientes import DatosCompartidos
import ProcesoPuerto

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
        self.inicio(Celda, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max)

    def inicio(self, Celda, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max):
        global FIN
        global PorSetear
        FIN = False
        PorSetear = None
        # modifico valores de condiciones de seteo solo si la celda no esta en proceso
        if self.CeldaLibre(Celda):
            self.ActualizoCondGuardado(Celda, False, float(Promedio))
            ActualizoMatriz(Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente )
            if self.ui.BotActivo.isChecked():
                PorSetear = Celda
                self.ui.BotSetearV.setChecked(False)
                self.ui.BotSetearC.setChecked(False)
            else:
                # ENVIO
                #EnviarPS_I(Corriente,False,str (Celda ))
                self.chequeaRB(Celda, True)
                fila = deque(maxlen=16000)  # definirlo aca implica que es el incicio
                datos = DatosCompartidos()
                self.ui.BotSetearV.setChecked(False)
                self.ui.BotSetearC.setChecked(False)
                self.ui.BotActivo.setChecked(True)
                # inicio lectura

                self.threadPool.append(ProcesoPuerto.LECTURA(fila, self.filaPloteo, datos))

                # self.disconnect(self.threadPool[len(self.threadPool)-1],
                # self.threadPool[len(self.threadPool)-1].signal, self.ActualValores)
                self.connect(self.threadPool[len(self.threadPool)-1],
                             self.threadPool[len(self.threadPool)-1].signal,
                             self.ActualValores)

                self.threadPool[len(self.threadPool)-1].start()
                time.sleep(0.5)
                # inicio procesamiento
                self.threadPool.append(PROCESO(fila))
                self.threadPool[len(self.threadPool)-1].start()
        else:
            print 'imposible setear celda no libre'

        if PorSetear is not None:
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

    def ActualizoCondGuardado(self, Celda, Activa, Promedio ):
        # ActualizoCondGuardado(      Celda, False, float(Promedio))
        global CondGuardado
        # print 'desde actualizo guardado la celda ' + str(Celda) + 'esta activa? ' + str(Activa)
        # self.chequeaRB(Celda, Activa)
        # print 'Actualizo  Guardado ' + str(Celda) + str(Activa)
        for i in range(len(string.ascii_letters)):
            if Celda == string.ascii_letters[i]:
                CondGuardado[i][1] = Activa
                CondGuardado[i][2] = Promedio
                break

    def PararCelda(self):  # adicionar mandar i=0 para cuando para celda usar por setear en 0
        global PorSetear
        # global CondSeteo
        Celda=self.ui.cmbCelPlot.currentText()
        print '\n\nfinalizada celda: '+str( Celda)+ ' por usuario\n\n'
        # self.ActualizoCondGuardado(Celda,False,0.0)
        ActualizoMatriz(Celda,0,0,0,1,0)
        # barridos 0 y corriente 0 y tiempoMax mayor a cero pero minimo
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

        self.Ploteo1.clear()
        self.Ploteo2.clear()
        self.Ploteo2.plot(ValX,  pen='r')
        self.Ploteo2.plot(ValY, pen='g')
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

    # def CeldaLibre(self, celda):
    #     global CondSeteo
    #     for i in range(len( string.ascii_letters)):
    #         if celda == string.ascii_letters[i]:
    #             if CondSeteo[i][4] != 0:
    #                 return False
    #                 break
    #             else:
    #                 return True
    #                 break


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

"""########################################################## CLASE PARA Procesamiento"""


class PROCESO(QtCore.QThread):
    def __init__(self, fila, parent=None):
        QtCore.QThread.__init__(self)
        self.DEPOSITO = fila

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        global FIN
        a = b = c = d = e = f = g = h = i = j = k = l = m = n = o = p = False
        while len(self.DEPOSITO) != self.DEPOSITO.maxlen:
            try:
                separado = self.DEPOSITO.popleft()
            except:
                separado[0] = '$'
                print "."
            if separado[0] != '$':
                Barrido = separado[1]
                Tension = separado[2]
                Corriente = separado[3]
                Tiempo = separado[4]

                if separado[0] == 'a':
                    a = self.CeldaA(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'b':
                    b = self.CeldaB(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'c':
                    c = self.CeldaC(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'd':
                    d = self.CeldaD(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'e':
                    e = self.CeldaE(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'f':
                    f = self.CeldaF(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'g':
                    g = self.CeldaG(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'h':
                    h = self.CeldaH(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'i':
                    i = self.CeldaI(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'j':
                    j = self.CeldaJ(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'k':
                    k = self.CeldaK(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'l':
                    l = self.CeldaL(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'm':
                    m = self.CeldaM(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'n':
                    n = self.CeldaN(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'o':
                    o = self.CeldaO(Barrido, Tension, Corriente, Tiempo)
                elif separado[0] == 'p':
                    p = self.CeldaP(Barrido, Tension, Corriente, Tiempo)
                else:
                    print '\n se recibio un caracter inesperado \n'
            todas = a or b or c or d or e or f or g or h or i or j or k or l or m or n or o or p
            if not todas == True:
                myapp.ui.BotActivo.setChecked(False)
                FIN = True
                print 'ninguna celda activa, saliendo de loop'
                break

    def CeldaA(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('a')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('a', False)
                CondGuardado[CeldaEnNum] = ['a', False, 0]
                self.CerrarCSV('a')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'a')
                    PaPromediar = []
                    return True
        else:
            return False

    def CeldaB(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('b')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('b', False)
                CondGuardado[CeldaEnNum] = ['b', False, 0]
                self.CerrarCSV('b')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'b')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaC(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('c')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('c', False)
                CondGuardado[CeldaEnNum] = ['c', False, 0]
                self.CerrarCSV('c')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'c')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaD(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('d')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('d', False)
                CondGuardado[CeldaEnNum] = ['d', False, 0]
                self.CerrarCSV('d')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'd')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaE(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('e')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('e', False)
                CondGuardado[CeldaEnNum] = ['e', False, 0]
                self.CerrarCSV('e')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'e')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaF(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('f')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('f', False)
                CondGuardado[CeldaEnNum] = ['f', False, 0]
                self.CerrarCSV('f')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'f')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaG(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('g')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('g', False)
                CondGuardado[CeldaEnNum] = ['g', False, 0]
                self.CerrarCSV('g')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'g')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaH(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('h')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('h', False)
                CondGuardado[CeldaEnNum] = ['h', False, 0]
                self.CerrarCSV('h')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'h')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaI(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('i')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('i', False)
                CondGuardado[CeldaEnNum] = ['i', False, 0]
                self.CerrarCSV('i')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'i')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaJ(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('j')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('j', False)
                CondGuardado[CeldaEnNum] = ['j', False, 0]
                self.CerrarCSV('j')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'j')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaK(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('k')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('k', False)
                CondGuardado[CeldaEnNum] = ['k', False, 0]
                self.CerrarCSV('k')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'k')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaL(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('l')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('l', False)
                CondGuardado[CeldaEnNum] = ['l', False, 0]
                self.CerrarCSV('l')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'l')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaM(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('m')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('m', False)
                CondGuardado[CeldaEnNum] = ['m', False, 0]
                self.CerrarCSV('m')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'm')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaN(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('n')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('n', False)
                CondGuardado[CeldaEnNum] = ['n', False, 0]
                self.CerrarCSV('n')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'n')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaO(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('o')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('o', False)
                CondGuardado[CeldaEnNum] = ['o', False, 0]
                self.CerrarCSV('o')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'o')
                    PaPromediar = []
                return True
        else:
            return False

    def CeldaP(self, Barrido, Tension, Corriente, Tiempo):
        global CondGuardado
        CeldaEnNum = NumDeCelda('p')
        """chequeo que promedio halla sido iniciado"""
        if CondGuardado[CeldaEnNum][2] != 0:
            """primer ingreso"""
            if not CondGuardado[CeldaEnNum][1]:
                global PaPromediar
                PaPromediar = []
                CondGuardado[CeldaEnNum][1] = True
            if Tension == Corriente == '%':
                print 'cierro archivo actualizo condiciones de guardado'
                myapp.chequeaRB('p', False)
                CondGuardado[CeldaEnNum] = ['p', False, 0]
                self.CerrarCSV('p')
                return False
            else:
                Promedio = CondGuardado[CeldaEnNum][2]
                PaPromediar += [Tension, Corriente, Tiempo],
                if len(PaPromediar) == (100 / Promedio):
                    Tension = Corriente = Tiempo = 0.0
                    for i in range(len(PaPromediar)):
                        Tension += PaPromediar[i][0]
                        Corriente += PaPromediar[i][1]
                        Tiempo += PaPromediar[i][2]
                    Tension = Tension / len(PaPromediar)
                    Corriente = Corriente / len(PaPromediar)
                    Tiempo = Tiempo / len(PaPromediar)
                    self.GuardaCSV([Barrido, Tension, Corriente, Tiempo], 'p')
                    PaPromediar = []
                return True
        else:
            return False

    def ReseteoTodas(self):
        global CondSeteo
        global CondGuardado
        CondGuardado = [['a', False, 0.0], ['b', False, 0.0], ['c', False, 0.0], ['d', False, 0.0], ['e', False, 0.0],
                        ['f', False, 0.0], ['g', False, 0.0], ['h', False, 0.0], ['i', False, 0.0], ['j', False, 0.0],
                        ['k', False, 0.0], ['l', False, 0.0], ['m', False, 0.0], ['n', False, 0.0], ['o', False, 0.0],
                        ['p', False, 0.0]]
        #            [celda, Activa?, Promediado]
        CondSeteo = [['a', 0, 0, 0, 0, 0], ['b', 0, 0, 0, 0, 0], ['c', 0, 0, 0, 0, 0], ['d', 0, 0, 0, 0, 0],
                     ['e', 0, 0, 0, 0, 0], ['f', 0, 0, 0, 0, 0], ['g', 0, 0, 0, 0, 0], ['h', 0, 0, 0, 0, 0],
                     ['i', 0, 0, 0, 0, 0], ['j', 0, 0, 0, 0, 0], ['k', 0, 0, 0, 0, 0], ['l', 0, 0, 0, 0, 0],
                     ['m', 0, 0, 0, 0, 0], ['n', 0, 0, 0, 0, 0], ['o', 0, 0, 0, 0, 0], ['p', 0, 0, 0, 0, 0]]
        # [celda, barr, vli, vls, tmax, corr]

    # def CerrarCSV(self, celda):  # ver como adicionar directorio
    #     encabezado = [' Barrido ', ' Tension[mV]', ' Corriente[uA] ', ' Tiempo[Seg] ']
    #     columna = [' ----- ', ' ----- ', ' ----- ', ' ----- ']
    #     nombre = 'Arch_Cn-' + str(celda) + '.csv'
    #     try:
    #         open(nombre, 'r')
    #         with open(nombre, 'a') as f:
    #             f_csv = csv.writer(f)
    #             f_csv.writerow(columna)
    #             f.close()
    #     except IOError:
    #         with open(nombre, 'w+') as f:
    #             f_csv = csv.writer(f)
    #             f_csv.writerow(encabezado)
    #             f_csv.writerow(columna)
    #             f.close()
    #
    # def GuardaCSV(self,     columna, celda):  # ver como adicionar directorio
    #     encabezado = [' Barrido ', ' Tension[mV]', ' Corriente[uA] ', ' Tiempo[Seg] ']
    #     nombre = 'Arch_Cn-' + str(celda) + '.csv'
    #     try:
    #         open(nombre, 'r')
    #         with open(nombre, 'a') as f:
    #             f_csv = csv.writer(f)
    #             f_csv.writerow(columna)
    #             f.close()
    #     except IOError:
    #         with open(nombre, 'w+') as f:
    #             f_csv = csv.writer(f)
    #             f_csv.writerow(encabezado)
    #             f_csv.writerow(columna)
    #             f.close()




"""########################################################## CLASE PARA Ploteo en tiempo real"""

class PLOTEOTR(pg.QtCore.QThread):
    newData1 = pg.QtCore.Signal(object)
    newData2 = pg.QtCore.Signal(object)

    def __init__(self, Celda, FilaPlot, parent=None):
        # QtCore.QThread.__init__(self)
        super(PLOTEOTR, self).__init__()
        self.Celda = Celda
        self.CONTENEDOR = FilaPlot

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        # global CondPaBarrer     #         [celda, barrido (actual), Tinicio]
        global FIN
        Listax = deque(maxlen=16000)
        Listay = deque(maxlen=16000)

        while True:

            if len(self.CONTENEDOR) == 0:
                print '-',
                # time.sleep(3)
                if len(self.CONTENEDOR) == 0:
                    print '-',
                    # time.sleep(3)
                    if len(self.CONTENEDOR) == 0:
                        print 'error pila vacia -ploteo- por mucho tiempo '
                        break
            separado = self.CONTENEDOR.popleft()
            if myapp.ui.BotParaPlot.isChecked() or FIN or separado[0] == '%':
                print 'saliendo del plot desde plot class'
                myapp.ui.BotParaPlot.setChecked(False)
                myapp.ui.RBTiemReal.setChecked(False)
                myapp.ui.LimPant()
                Listax = []
                Listay = []
                break
            if separado[0] == str(self.Celda):
                Tension = separado[2]
                Corriente = separado[3]
                Listax.append(Tension)  # tension
                Listay.append(Corriente)  # corriente
                data1 = Listax
                data2 = Listay
                self.newData1.emit(data1)
                self.newData2.emit(data2)
                # time.sleep(0.05)
                """buscar otra forma de controlarlo evitando entrar en los botones"""


if __name__=="__main__":
    app=QtGui.QApplication(sys.argv)
    global ser
    myapp = Myform()
    myapp.show()
    sys.exit(app.exec_())
