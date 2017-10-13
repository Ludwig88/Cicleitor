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

        self.Ploteo1 = self.ui.plot.addPlot(row=0, col=0)
        self.Ploteo2 = self.ui.plot.addPlot(row=1, col=0)

        self.threadPool = []

        self.filaPloteo = deque(maxlen=16000)

        self.ui.BotActivo.setCheckable(True)
        self.ui.BotSetearC.setCheckable(True)
        self.ui.BotSetearV.setCheckable(True)
        self.ui.BotParaPlot.setCheckable(True)

    def inicioVOC(self):
        Celda = self.ui.cmbCelV.currentText()
        Promedio = float(self.ui.cmbPromV.currentText())
        T_Max = int(self.ui.LinEdTiemV.text())
        Datos.xIniciaVoc(Celda, Promedio, T_Max)
        self.inicio(Celda) #, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max

    def inicioCiclado(self):
        # seteo valores para el proceso
        Celda = self.ui.cmbCelC.currentText()
        Promedio = float(self.ui.cmbProm.currentText())
        Corriente = int(self.ui.LinEdCorri.text())
        Ciclos = int(self.ui.LinEdCiclos.text())
        V_lim_inf = int(self.ui.LinEdVLInf.text())
        V_lim_sup = int(self.ui.LinEdVLSup.text())
        T_Max = int(self.ui.LinEdTMax.text())
        if Corriente > 0 :
            CargaOdescarga = True
        else:
            CargaOdescarga = False
        Datos.xCondicionesDeGuardado(Celda, Ciclos, V_lim_sup, V_lim_inf, T_Max, Corriente, Promedio, CargaOdescarga)
        self.inicio(Celda) #Celda, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max

    def inicio(self, Celda): #, Celda, Promedio, Corriente, Ciclos, V_lim_inf, V_lim_sup, T_Max
        if not Datos.xIsActive(Celda):
            if self.ui.BotActivo.isChecked():
                self.ui.BotSetearV.setChecked(False)
                self.ui.BotSetearC.setChecked(False)
                Datos.xEnviarPS(Celda)
            else:
                #Iniciar Ciclado con start de Datos
                self.chequeaRB(Celda, True)
                self.ui.BotSetearV.setChecked(False)
                self.ui.BotSetearC.setChecked(False)
                self.ui.BotActivo.setChecked(True)
                Datos.PrimerInicio()
                time.sleep(0.5) #ver si es necesario!
                Datos.xEnviarPS(Celda)
                barrido, Vin, Iin, Tiem = Datos.xGetValTiempoReal(Celda)
                self.connect(self.threadPool[len(self.threadPool) - 1],
                             self.threadPool[len(self.threadPool) - 1].signal,
                             self.ActualValores(barrido, Vin, Iin, Tiem))

        else:
            print 'Ciclador - imposible setear celda no libre'

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

    def PararCelda(self):
        celda = self.ui.cmbCelPlot.currentText()
        Datos.xPararCelda(celda)

    def ActCondUi(self):
        Celda=self.ui.cmbCelC.currentText()
        (corriente, ciclos, vli, vls, tmax, prom) = Datos.xGetCondGuardado(Celda)
        reng=NumDeCelda(Celda)
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


def NumDeCelda(celda):
    for i in range(len(string.ascii_letters)):
        if celda == string. ascii_letters[i]:
            return i
            break


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
    global Datos
    Datos = DatosCompartidos()
    myapp = Myform()
    myapp.show()
    sys.exit(app.exec_())
