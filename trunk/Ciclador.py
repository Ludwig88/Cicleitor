#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'debug/Log.txt')
log = open(filename, "a+")

GraphicInterface = os.path.join(dir, 'graphics/CicladorIG-3.ui')

import csv  # , resource
import pyqtgraph as pg
import string
import sys, datetime
import time
from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QMutex
from PyQt4.uic import *
from collections import deque  # double ended queue
import DatosIndependientes
import ProcesoPuerto
import PLOTEOTR

"""########################################################## CLASE PARA settings de plot"""
##### Override class #####
class NonScientific(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super(NonScientific, self).__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [int(value*1) for value in values] #This line return the NonScientific notation value



"""########################################################## CLASE PARA IU"""


class Myform(QtGui.QMainWindow):

    def __init__(self, parent=None):
        locale = unicode(QtCore.QLocale.system().name())
        QtGui.QWidget.__init__(self, parent)
        self.ui = loadUi(GraphicInterface, self)

        self.flagVTR = False
        self.flagPLOTVTR = False

        self.Ploteo1 = self.ui.plot.addPlot(row=0, col=0, axisItems={'left': NonScientific(orientation='left')})
        self.Ploteo2 = self.ui.plot.addPlot(row=1, col=0, axisItems={'left': NonScientific(orientation='left')})

        self.threadPool = []

        self.threadOne = [] #DatosIndependietes DatosCompartidos
        self.threadTwo = [] #PLOTEOTR

        self.mutex = QMutex()

        self.filaPloteo = deque(maxlen=16000)
        self.filaDatos = deque(maxlen=16000)
        self.dequeSetting = deque(maxlen=100)

        self.threadOne.append(DatosIndependientes.DatosCompartidos(self.dequeSetting, self.filaPloteo))

        print("valor de len de thread one menos 1 es " + str(len(self.threadOne) - 1), file=log)
        self.threadOne[len(self.threadOne) - 1].start()

        self.connect(self.threadOne[len(self.threadOne) - 1],
                     self.threadOne[len(self.threadOne) - 1].signal,
                     self.ActualValores)
        self.connect(self.threadOne[len(self.threadOne) - 1],
                     self.threadOne[len(self.threadOne) - 1].signalSingleShot,
                     self.LlenoCamposCondGuardado)
        #QObject.connect(QObject, SIGNAL(), QObject, SLOT(), Qt.ConnectionType = Qt.AutoConnection) -> bool
        self.connect(self.threadOne[len(self.threadOne) - 1],
                     self.threadOne[len(self.threadOne) - 1].parocelda,
                     self.PararCelda)

        self.ui.BotActivo.setCheckable(True)
        self.ui.BotSetearC.setCheckable(True)
        self.ui.BotSetearV.setCheckable(True)
        self.ui.BotParaPlot.setCheckable(True)

        self.ui.AYUDA.append('<a href="ayuda/readme.html"> AYUDA </a>')

    def inicioVOC(self):
        Celda = unicode(self.ui.cmbCelV.currentText())
        Promedio = float(self.ui.cmbPromV.currentText())
        T_Max = int(self.ui.LinEdTiemV.text())
        print( "["+str(datetime.datetime.now())+"][UICICL] datos " + str(["SETV", str(Celda), 1, 999999, -999999, T_Max, 0, Promedio, False]),file=log)
        self.mutex.lock()
        self.dequeSetting.append(["SETV", str(Celda), 1, 999999, -999999, T_Max, 0, Promedio, False])
        self.mutex.unlock()
        self.inicio(Celda)

    def inicioCiclado(self):
        # seteo valores para el proceso
        Celda = self.ui.cmbCelC.currentText()
        Promedio = float(self.ui.cmbProm.currentText())
        Corriente = int(self.ui.LinEdCorri.text())
        Ciclos = int(self.ui.LinEdCiclos.text())
        V_lim_inf = float(self.ui.LinEdVLInf.text()) * 1000
        V_lim_sup = float(self.ui.LinEdVLSup.text()) * 1000
        T_Max = int(self.ui.LinEdTMax.text())
        if Corriente > 0:
            CargaOdescarga = True
        else:
            CargaOdescarga = False
        print("["+str(datetime.datetime.now())+"][UICICL] datos " + str(["SETC", Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga]), file=log)
        #print("["+str(datetime.datetime.now())+"UICICL] datos " + str(
        #    ["SETC", Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga]))
        self.mutex.lock()
        self.dequeSetting.append(["SETC", Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga])
        self.mutex.unlock()
        self.inicio(Celda)  # Celda, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max
        # self.connect(self.threadPool[len(self.threadPool) - 1],
        #              self.threadPool[len(self.threadPool) - 1].signal,
        #              self.ActualValores)
        # self.connect(self.threadOne[len(self.threadOne) - 1],
        #              self.threadOne[len(self.threadOne) - 1].signal,
        #              self.ActualValores)
        # self.connect(self.threadOne[len(self.threadOne) - 1],
        #              self.threadOne[len(self.threadOne) - 1].signalSingleShot,
        #              self.LlenoCamposCondGuardado)

    def inicio(self, Celda):
        if self.ui.BotActivo.isChecked():
            self.ui.BotSetearV.setChecked(False)
            self.ui.BotSetearC.setChecked(False)
            # self.ui.labelInfo("no puedo setear la celda")
        else:
            #Iniciar Ciclado con start de Datos
            self.ui.BotSetearV.setChecked(False)
            self.ui.BotSetearC.setChecked(False)
            self.ui.BotActivo.setChecked(True)
        self.chequeaRB(Celda, True)

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

    def PararCelda(self, Celda=None):
        if Celda is None:
            Celda = self.ui.cmbCelC.currentText()
        print("["+str(datetime.datetime.now())+"UICICL] datos " + str(["FINV", Celda, 0, 0, 0, 0, 0, 0, False]), file=log)
        self.mutex.lock()
        self.dequeSetting.append(["FINV", Celda, 0, 0, 0, 0, 0, 0, False])
        self.mutex.unlock()
        self.chequeaRB(Celda, False)

    def ActCondUi(self):
        Celda=self.ui.cmbCelC.currentText()
        print("["+str(datetime.datetime.now())+"][UICICL] datos " + str(["AUI", Celda, None, None, None, None, None, None, None]), file=log)
        self.mutex.lock()
        self.dequeSetting.append(["AUI", Celda, None, None, None, None, None, None, None])
        self.mutex.unlock()

    def LlenoCamposCondGuardado(self, corriente, ciclos, vli, vls, tmax, prom):
        self.ui.LinEdCorri.setText(str(corriente))
        self.ui.LinEdCiclos.setText(str(ciclos))
        self.ui.LinEdVLInf.setText(str(vli))
        self.ui.LinEdVLSup.setText(str(vls))
        self.ui.LinEdTMax.setText(str(tmax))
        if prom == 100:
            self.ui.cmbProm.setCurrentIndex(7)
            self.ui.cmbProm.setCurrentIndex(6)
        elif prom == 25:
            self.ui.cmbProm.setCurrentIndex(5)
        elif prom == 10:
            self.ui.cmbProm.setCurrentIndex(4)
        elif prom == 5:
            self.ui.cmbProm.setCurrentIndex(3)
        elif prom == 1:
            self.ui.cmbProm.setCurrentIndex(2)
        elif prom == 0.5:
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
        self.ui.LinEdVLInf.setText('-999.999')
        self.ui.LinEdVLSup.setText('999.999')
        self.ui.LinEdTMax.setText('12')
        self.ui.cmbProm.setCurrentIndex(7)

    def PararGrafico(self):
        Celda = self.ui.cmbCelPlot.currentText()
        print("["+str(datetime.datetime.now())+"][CICL] Parar plot para " + str(Celda), file=log)
        self.mutex.lock()
        self.dequeSetting.append(["FPlot", Celda, None, None, None, None, None, None, None])
        self.mutex.unlock()

    def ValTiempoReal(self):
        Celda = self.ui.cmbCelTReal.currentText()
        self.mutex.lock()
        self.flagVTR = not self.flagVTR
        if self.flagVTR:
            print("["+str(datetime.datetime.now())+"][CICL] inicia val en tiempo REAL con " + str(Celda), file=log)
            self.dequeSetting.append(["VTR", Celda, None, None, None, None, None, None, None])
        else:
            print("["+str(datetime.datetime.now())+"][CICL] Finaliza val en tiempo REAL con " + str(Celda), file=log)
            self.dequeSetting.append(["FTR", Celda, None, None, None, None, None, None, None])
        self.mutex.unlock()

    def ActualValores(self, barrido, Vin, Iin, Tiem, TiempoTotal, Ingresos):
        if barrido != 0 and Vin != 0 and Iin != 0 and Tiem != 0 and Ingresos != 0:
            #print("["+str(datetime.datetime.now())+"][CICL] -val-", file=log)
            barridos_real = (int(barrido) / 2) + (int(barrido) % 2)
            self.ui.SalBarrido.setText(str(barridos_real))
            self.ui.SalVInst.setText(str(int(Vin) / 1000.0))
            self.ui.SalIInst.setText(str(int(Iin) / 1000000.0))
            self.ui.SalTiemp.setText(str('{:014.2f}'.format(float(Tiem))))
            self.ui.SalTiempTot.setText(str('{:015.1f}'.format(float(TiempoTotal))))
            self.ui.SalMuestrasInst.setText(str(Ingresos))
        else:
            print("["+str(datetime.datetime.now())+"][CICL] Actualizo valores - FIN", file=log)

    """ ############################################################## PLOTEO """
    def LimPant(self):
        self.Ploteo1.clear()
        self.Ploteo2.clear()

    def Plot(self):
        Celda = self.ui.cmbCelPlot.currentText()
        if self.ui.RBTiemReal.isChecked():
            print("["+str(datetime.datetime.now())+"][CICL_PLOT] Starts plot en tiempo REAL", file=log)
            self.mutex.lock()
            self.flagPLOTVTR = not self.flagPLOTVTR
            if self.flagPLOTVTR:
                self.dequeSetting.append(["Plot", Celda, None, None, None, None, None, None, None])
            else:
                self.dequeSetting.append(["FPlot", None, None, None, None, None, None, None, None])
            self.mutex.unlock()

            ploteo1 = self.Ploteo1.plot()
            ploteo2 = self.Ploteo2.plot()

            self.threadTwo.append(PLOTEOTR.PLOTEOTR(Celda, self.filaPloteo))
            self.threadTwo[len(self.threadTwo)-1].newData1.connect(self. update1)
            self.threadTwo[len(self.threadTwo)-1].newData2.connect(self. update2)
            self.threadTwo[len(self.threadTwo)-1].start()

        elif self .ui.RBPlotFin.isChecked():
            listaBarr = str(self.ui.LELisBarridos.text())
            listaBarr = listaBarr.split(',')
            self.PlotFinal(str(Celda),listaBarr)

        elif self .ui.RDdefinido.isChecked():
            Inicial = int(self.ui.LEBarIn.text())
            Final = int(self.ui.LEBarFin.text())
            self.PlotEntreVal(Inicial,Final,Celda)

        elif self.ui. RBCapac.isChecked():
            PesoAnodo = float(self.ui.LEPesoAnodo. text ())
            self.PlotFinalCapacidades(Celda,PesoAnodo)

    def update1(self, data1):
        self.Ploteo1.plot(data1,pen='g',clear=True)  # data2,clear=True)
        self.Ploteo1.setLabel('left', text='Tension', units='mV', unitPrefix=None)
        self.Ploteo1. showGrid(x=True, y=True, alpha=None)
        # setLabel(axis, text=None, units=None, unitPrefix=None, **args)

    def update2(self, data2):
        self.Ploteo2.plot(data2, pen='r', clear=True)
        self.Ploteo2.setLabel('left', text='Corriente', units='uA', unitPrefix=None)
        self.Ploteo2.showGrid(x=True, y=True, alpha=None)

    def PlotFinal(self, Celda, barridos):
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
            print( str(len(DequePLOT)),file=log)
            for i in range(len(DequePLOT)-2):
                if DequePLOT[i][0] >= j:
                    if DequePLOT[i][3]==0 and len(ValT)!=0 :
                        self.Ploteo1.plot(ValT, ValX , pen=(j,len(barridos)))
                        print( 'carga ' + str(len(ValT)),file=log)
                        ValT=[]
                        ValX=[]
                        ValT+=DequePLOT [i][3],
                        ValX+=DequePLOT[i][1],  # tension
                    else :
                        ValT+=DequePLOT[i][3] ,
                        ValX+=DequePLOT[i][1],  # tension
                if DequePLOT[i][0]>j:
                    print( 'descarga ' + str(len(ValT)),file=log)
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
        print( 'barrido ultimo: '+str(barridoMax),file=log)

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
        print( ValCapacidades,file=log)
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
        self.Ploteo2.setLabel('left', text='Corriente', units='uA', unitPrefix=None)
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


def NumDeCelda(celda):
    for i in range(len(string.ascii_letters)):
        if celda == string. ascii_letters[i]:
            return i
            break

if  __name__  ==  "__main__" :
    app = QtGui.QApplication(sys.argv)
    myapp = Myform()
    myapp.show()
    sys.exit(app.exec_())
