#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtCore

import csv



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

    def CerrarCSV(self, celda):  # ver como adicionar directorio
        encabezado = [' Barrido ', ' Tension[mV]', ' Corriente[uA] ', ' Tiempo[Seg] ']
        columna = [' ----- ', ' ----- ', ' ----- ', ' ----- ']
        nombre = 'Arch_Cn-' + str(celda) + '.csv'
        try:
            open(nombre, 'r')
            with open(nombre, 'a') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(columna)
                f.close()
        except IOError:
            with open(nombre, 'w+') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(encabezado)
                f_csv.writerow(columna)
                f.close()

    def GuardaCSV(self, columna, celda):  # ver como adicionar directorio
        encabezado = [' Barrido ', ' Tension[mV]', ' Corriente[uA] ', ' Tiempo[Seg] ']
        nombre = 'Arch_Cn-' + str(celda) + '.csv'
        try:
            open(nombre, 'r')
            with open(nombre, 'a') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(columna)
                f.close()
        except IOError:
            with open(nombre, 'w+') as f:
                f_csv = csv.writer(f)
                f_csv.writerow(encabezado)
                f_csv.writerow(columna)
                f.close()