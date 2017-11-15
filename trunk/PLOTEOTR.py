#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyqtgraph as pg

import time

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

    def __del__(self):
        self.wait()  # This will (should) ensure that the thread stops processing before it gets destroyed.

    def run(self):
        # global CondPaBarrer     #         [celda, barrido (actual), Tinicio]
        Listax = deque(maxlen=16000)
        Listay = deque(maxlen=16000)

        while True:
            if len(self.CONTENEDOR) != 0:
                time.sleep(0.001)
                separado = self.CONTENEDOR.popleft()
                # if myapp.ui.BotParaPlot.isChecked() or separado[0] == '%':
                #     print 'saliendo del plot desde plot class'
                #     myapp.ui.BotParaPlot.setChecked(False)
                #     myapp.ui.RBTiemReal.setChecked(False)
                #     myapp.ui.LimPant()
                #     Listax = []
                #     Listay = []
                #     break
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

