import os
import sys
import time
import csv

import pandas as pd
from PyQt4 import QtGui, QtCore

t = time.localtime()
date = "{0}-{1}-{2}".format(t[0],t[1],t[2])
lesson = "lesson{}.log".format(date)
table_path = "1652-KTPO-1415-2.txt"
db_path = "1652-1415-2.txt"


class Table(QtGui.QTableWidget):
    def __init__(self, thestruct, *args):
        QtGui.QTableWidget.__init__(self, *args)
        self.data = thestruct    # dict or DataFrame
        self.setmydata()

    def setmydata(self):
        for n, key in enumerate(reversed(sorted(self.data))):
            for m, item in enumerate(self.data[key]):
                newitem = QtGui.QTableWidgetItem(str(item))
                self.setItem(m, n, newitem)
        self.setHorizontalHeaderLabels(list(reversed(sorted(self.data))))


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(550, 350)
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
                  (screen.height()-size.height())/2)
        self.setWindowTitle('Students')

        self.enter = QtGui.QAction('Enter in system', self, statusTip='Enter',
                                shortcut='Ctrl+E', triggered=self.login)
        self.open = QtGui.QAction('Open table', self, statusTip='OpenDB',
                                shortcut="Ctrl+O", triggered=self.openDB)
        self.save = QtGui.QAction('Save table', self, statusTip='SaveDB',
                                shortcut="Ctrl+S", triggered=self.saveDB)
        self.exit = QtGui.QAction('Close app', self, statusTip="Close app",
                                shortcut='Ctrl+Q', triggered=self.close)
        self.startLes = QtGui.QAction('Start lesson', self,
                        statusTip='Start lesson', triggered=self.startLesson)
        self.endLes = QtGui.QAction('End lesson', self, statusTip='End lesson',
                                triggered=self.endLesson)
        self.markSelf = QtGui.QAction('Mark', self, statusTip='Mark Self',
                                triggered=self.mark)
        self.menubar = self.menuBar()
        self.fl = self.menubar.addMenu('&File')
        self.fl.addAction(self.enter)
        self.fl.addAction(self.exit)

        font = QtGui.QFont('Times', 42, 5, False)
        self.grat = QtGui.QLabel('Welcome to\n lesson!')
        self.grat.setFont(font)
        self.grat.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.grat)

        self.editor = self.log = self.pas = self.access = 0

        self.statusBar().showMessage('Ready')

    def openDB(self):
        self.qtable = Table(table, table.shape[0], table.shape[1])
        self.setCentralWidget(self.qtable)

    def saveDB(self):
        try:
            with open(table_path, 'w') as stream:
                cLinea = ''
                for k in self.qtable.data:
                    cLinea += k + ";"
                cLinea = cLinea[:-1] + '\n'
                stream.write(cLinea)
                cLinea = ''

                for fila in range(self.qtable.rowCount()):
                    for columna in range(self.qtable.columnCount()):
                        cLinea += str(self.qtable.item(fila, columna).data(QtCore.Qt.DisplayRole)) + ';'
                    cLinea = cLinea[:-1] + "\n"
                    stream.write(cLinea)
                    cLinea = ''
        except NameError as e:
            self.message('Nothing to save!','Error')
            print(e)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                 "Are you sure to quit?", QtGui.QMessageBox.No,
                 QtGui.QMessageBox.Yes)
        if reply == QtGui.QMessageBox.Yes: event.accept() 
        else: event.ignore()
    
    def login(self):
        try:
            while not(self.access):
                self.log, self.pas, ok = LoginDialog.getLoginPass()
                if not(ok):
                    break
                elif ((self.log==capLogin)&(self.pas==capPassword)) | \
                     ((self.log==teachLogin)&(self.pas==teachPassword)):
                    self.access = 2   # teacher
                    self.fl = self.menubar.addMenu('&Lesson')
                    self.fl.addAction(self.open)
                    self.fl.addAction(self.save)
                    self.fl.addAction(self.startLes)
                    self.fl.addAction(self.endLes)
                    self.message('Welcome, master!', 'Message')
                    break
                elif db[db.Login==int(self.log)].empty or \
                  not((db[db.Login==int(self.log)].Password==self.pas).bool()):
                    self.access = 0 
                    self.message('Wrong login or password!', 'Error')
                else:
                    self.access = 1   # ok
                    self.fl = self.menubar.addMenu('&Lesson')
                    self.fl.addAction(self.markSelf)
            else:
                self.message('You\'re in', 'Message')
            if self.access and self.log==capLogin:
                self.fl.addAction(self.markSelf)
        except Exception as e:
            self.access = 0
            self.message('Unexpected Error: {0}'.format(e), 'Error')

    def message(self, message, name):
        reply = QtGui.QMessageBox.question(self, name,
                                         message, QtGui.QMessageBox.Yes)

    def startLesson(self):
        if os.path.isfile(lesson):
            self.message("Lesson's already begun", 'Error')
        else:
            with open(lesson, 'w') as les: les.write(date)
            self.message('Lesson has begun', 'Message')
            table[date] = pd.Series([0 for _ in range(len(table))])
            table.to_csv(table_path,sep=';')
            self.openDB()

    def endLesson(self):
        if not(os.path.isfile(lesson)): 
            self.message("Now it isn't lesson", 'Error')
        else:
            os.remove(lesson)
            self.message('Lesson ends', 'Message')

    def mark(self):
        if os.path.isfile(lesson):
            for i in range(len(table)): 
                if table.loc[i].Login == int(self.log):
                    if table.loc[i][date]:
                        self.message("You've been checked already",'Error')
                    else:
                        table.loc[i][date] = 1
                        self.message("Congratulation! You've been checked",
                                     'Message')
            table.to_csv(table_path,sep=';')
        else:
            self.message("Now it isn't lesson", 'Error')


class LoginDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        self.login = QtGui.QLineEdit(self)
        self.passw = QtGui.QLineEdit(self, echoMode=2)
        buttons = QtGui.QDialogButtonBox(
                QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
                QtCore.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QtGui.QFormLayout(self)
        layout.addRow('Login', self.login)
        layout.addRow('Password', self.passw)
        layout.addRow(buttons)
    
    def getLogin(self):
        return (self.login, self.passw)

    @staticmethod
    def getLoginPass(parent=None):
        dialog = LoginDialog(parent)
        result = dialog.exec_()
        login, passw = dialog.getLogin()
        return (login.text(), passw.text(), result==QtGui.QDialog.Accepted)


def addTable():
    global table
    table = db[['Login']][:-1]
    with open(table_path, 'w') as tab:
        tab.write('Login\n')
        for x in range(len(db)-1):
            tab.write(str(db.loc[x].Login)+'\n')


def openTable():
    global table
    table = pd.read_csv(table_path, sep=';')
    if table.columns[0] != 'Login':
        table = table.drop(table.columns[0],axis=1)


def openDB():
    global db, capLogin, capPassword, teachLogin, teachPassword
    db = pd.read_csv(db_path, sep=';', header=None,
           names=['Surname','Name','SecondName','Login','Password'])
    capLogin, capPassword = str(db.irow(-2).Login), db.irow(-2).Password
    teachLogin, teachPassword = str(db.irow(-1).Login), db.irow(-1).Password
    if teachLogin=='0': teachLogin='000000'


if __name__ == "__main__":
    openDB()
    if not(os.path.isfile(table_path)):
        addTable() 
    else:
        openTable()
    app = QtGui.QApplication(sys.argv)
    """
    tb = Table(table, table.shape[0], table.shape[1])
    tb.show()
    """
    main = MainWindow()
    main.show()
    app.exec_()
