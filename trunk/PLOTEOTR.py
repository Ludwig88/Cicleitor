#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import os
dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'debug/Log.txt')
log = open(filename, "a+")

import time
import pyqtgraph as pg
from PyQt4.Qt import QMutex
from collections import deque  # double ended queue

#from Ciclador import myapp

class PLOTEOTR(pg.QtCore.QThread):
    newData1 = pg.QtCore.Signal(object)
    newData2 = pg.QtCore.Signal(object)

    def __init__(self, Celda, FilaPlot, parent=None):
        # QtCore.QThread.__init__(self)
        super(PLOTEOTR, self).__init__()
        self.Celda = Celda
        self.CONTENEDOR = FilaPlot
        self.mutex = QMutex()
        self.Active = True

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        # global CondPaBarrer     #         [celda, barrido (actual), Tinicio]
        Listax = deque(maxlen=16000)
        Listay = deque(maxlen=16000)
        print("runing start", file=log)

        while self.Active:
            time.sleep(0.01)
            if int(len(self.CONTENEDOR)) >= 1:
                #time.sleep(0.01)
                self.mutex.lock()
                separado = self.CONTENEDOR.popleft()
                self.mutex.unlock()
                if separado[0] == str(self.Celda):
                    if separado[1] == 0 and separado[2] == 0 and separado[3] == 0 :
                        self.Active = False
                        print("Parando PloteoTR", file=log)
                    Tension = separado[2] * (0.001)
                    Corriente = separado[3] * (0.001)
                    Listax.append(Tension)  # tension
                    Listay.append(Corriente)  # corriente
                    data1 = Listax
                    data2 = Listay
                    self.newData1.emit(data1)
                    self.newData2.emit(data2)
                    # time.sleep(0.05)
                    """buscar otra forma de controlarlo evitando entrar en los botones"""

