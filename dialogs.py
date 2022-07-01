import sys
import os
import sqlite3

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QTextEdit, QLabel, QComboBox

path = os.path.dirname(__file__)
#qtCreatorFile = "assets/NewProj.ui"
#Ui_Dialog, _ = uic.loadUiType(os.path.join(path, qtCreatorFile))

class NewProjDialog(QDialog):
    def __init__(self):
        super(NewProjDialog, self).__init__()
        #self.setupUi(self)
        uic.loadUi("assets/NewProj.ui", self)
        #find textBoxes
        self.titleText = self.findChild(QTextEdit, "titleText")
        self.descText = self.findChild(QTextEdit, "descText")

    def getValues(self):
        if self.exec_() == QDialog.Accepted:
            # get all values
            title = self.titleText.toPlainText()
            desc = self.descText.toPlainText()
            return title, desc
        else:
            return None

class OpenProjDialog(QDialog):
    def __init__(self):
        super(OpenProjDialog, self).__init__()
        uic.loadUi("assets/OpenProj.ui", self)
        self.projCombo = self.findChild(QComboBox, "projCombo")
        self.descLabel = self.findChild(QLabel, "descLabel")
        self.descLabel.setWordWrap(True)
        self.currentId = 0
        con = sqlite3.connect("bugtracker.db")
        cur = con.cursor()
        cur.execute("SELECT * FROM Projects")
        self.data = cur.fetchall()
        con.close()
        titles = [x[1] for x in self.data] #select returns tuple, only get first element of tuple
        self.desc = [x[2] for x in self.data] #3rd element returns description
        self.projCombo.addItems(titles)
        self.descLabel.setText(self.desc[0])

        self.projCombo.currentIndexChanged.connect(self.updateDesc)

    def updateDesc(self, index):
        self.descLabel.setText(self.desc[index])
        #also updating the id whilst here.
        self.currentId = self.data[index][0]

    def getIndex(self):
        if self.exec_() == QDialog.Accepted:
            # get all values
            title = self.projCombo.currentText()
            print("changed")
            return self.currentId
        else:
            return None


class IssueAndSchedule(QDialog):
    def __init__(self, typeToAdd):
        super(IssueAndSchedule, self).__init__()
        uic.loadUi("assets/Add.ui", self)
        self.priorityCombo = self.findChild(QComboBox, "priorityCombo")
        self.typeCombo = self.findChild(QComboBox, "typeCombo")
        self.titleText = self.findChild(QTextEdit, "titleText")
        self.descText = self.findChild(QTextEdit, "descText")
        self.values = [0, 0, 0, 0]
        if(typeToAdd == "Schedules"):
            self.typeCombo.clear()
            comboList = ["Feature", "Error Handling", "Optimization", "Unit Test"]
            self.typeCombo.addItems(comboList)

    def getValues(self):
        if self.exec_() == QDialog.Accepted:
            self.values[0] = self.titleText.toPlainText()
            self.values[1] = self.descText.toPlainText()
            self.values[2] = self.typeCombo.currentText()
            self.values[3] = self.priorityCombo.currentText()
            return self.values
        else:
            return None


