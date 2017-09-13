#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4 import QtGui

import sys, Ciclador

if __name__=="__main__":
    app=QtGui.QApplication(sys.argv)
    global ser
    ser=SeteoPuerto()
    myapp = Myform()
    myapp.show()
    sys.exit(app.exec_())