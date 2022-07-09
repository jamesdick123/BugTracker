import sys
import sqlite3
import os

from PyQt5 import uic
from PyQt5.QtWidgets import *
from dialogs import NewProjDialog, OpenProjDialog, IssueAndSchedule

loadedProjId = None

class ui(QMainWindow):
    def __init__(self):
        super(ui, self).__init__()
        #load ui file
        uic.loadUi("assets/window.ui", self)
        #finding items
        self.fileMenu = self.findChild(QMenu, "menuFile")
        self.newProjectAction = self.findChild(QAction, "actionNewProject")
        self.openProjectAction = self.findChild(QAction, "actionOpenProject")
        self.projLabel = self.findChild(QLabel, "projLabel")
        self.addIssueAction = self.findChild(QAction, "actionAddIssue")
        self.addScheduleAction = self.findChild(QAction, "actionAddSchedule")
        self.removeAction = self.findChild(QAction, "actionRemoveTask")
        self.issueTable = self.findChild(QTableWidget, "issueTable")
        self.scheduleTable = self.findChild(QTableWidget, "scheduleTable")
        self.tabSelector = self.findChild(QTabWidget, "bugTab")
        #menu button implementation
        self.newProjectAction.setShortcut('Ctrl+N')
        self.newProjectAction.triggered.connect(self.newProject)
        self.openProjectAction.setShortcut('Ctrl+O')
        self.openProjectAction.triggered.connect(self.openProject)
        self.removeAction.triggered.connect(self.removeTask)
        self.addIssueAction.triggered.connect(self.issueOrSchedule)
        self.addScheduleAction.triggered.connect(self.issueOrSchedule)
        #setting up table sizes
        self.issueTable.setWordWrap(True)
        horizontalHeader = self.issueTable.horizontalHeader()
        horizontalHeader.resizeSection(0, 120)
        horizontalHeader.resizeSection(1, 550)
        horizontalHeader.resizeSection(2, 100)
        horizontalHeader.resizeSection(3, 90)
        horizontalHeader = self.scheduleTable.horizontalHeader()
        horizontalHeader.resizeSection(0, 120)
        horizontalHeader.resizeSection(1, 550)
        horizontalHeader.resizeSection(2, 100)
        horizontalHeader.resizeSection(3, 90)

        #show window always put last before methods
        self.show()

    def newProject(self):
        print("temp")
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setWindowTitle("Error")
        p = NewProjDialog()
        try:
            title, desc = p.getValues()
            #no blank fields
            if(title == "" or desc == ""):
                error.setText("Disallowed text in title or description. These fields can't be blank")
                error.exec()
            else:
                #if not blank input
                con = sqlite3.connect('bugtracker.db')
                cur = con.cursor()
                cur.execute("INSERT INTO Projects VALUES (?, ?, ?)", (None, title, desc))
                con.commit()
                con.close()
                print(title + " " + desc)
        except TypeError: #type error is when none is received ie pressing cancel.. can't think of another way
            pass #cancel means they don't want an input anyway
        except Exception as err:
            error.setText("Unknown error: " + str(err))
            error.exec()

    def openProject(self):
        global loadedProjId
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setWindowTitle("Error")
        try:
            p = OpenProjDialog()
            loadedProjId = p.getIndex()
        except IndexError:
            error.setText("No projects found, try creating one instead.")
            error.exec()
        except Exception as err:
            error.setText("Unexpected error occured: " + str(err))
            error.exec()
        if loadedProjId != None: #don't need to check for blank values this time so this works
            con = sqlite3.connect("bugtracker.db")
            cur = con.cursor()
            cur.execute("SELECT Name FROM Projects WHERE ID='" + str(loadedProjId) + "'")
            data = cur.fetchall()
            self.projLabel.setText("Project: " + data[0][0])
            print(loadedProjId)
            con.close()
            #do method to fill data; keep the open project limited to just the dialog
            self.fillTable()

    def issueOrSchedule(self):
        if(loadedProjId == None):
            error = QMessageBox()
            error.setIcon(QMessageBox.Critical)
            error.setWindowTitle("Error")
            error.setText("No project currently selected, select or create a project in the file menu to add issues "
                          "or schedule tasks")
            error.exec()
        else:
            sender = self.sender()
            values = []
            typeToAdd = "Schedules"
            if(sender == self.addIssueAction):
                typeToAdd = "Issues"
            p = IssueAndSchedule(typeToAdd)
            values = p.getValues()
            if(values != None):
                con = sqlite3.connect("bugtracker.db")
                cur = con.cursor()
                cur.execute("INSERT INTO " + typeToAdd + " VALUES (?, ?, ?, ?, ?)", (None, values[0], values[1], values[2], values[3]))
                con.commit()
                #then need to get the ID of it, to add to
                cur.execute("SELECT ID FROM " + typeToAdd + " ORDER BY ID DESC LIMIT 0,1")
                data = cur.fetchall()
                cur.execute("INSERT INTO Project" + typeToAdd + " VALUES (?, ?, ?)", (None, loadedProjId, data[0][0]))
                con.commit()
                con.close()
                self.fillTable()



    def fillTable(self):
        conn = sqlite3.connect("bugtracker.db")
        cur = conn.cursor()
        #first does issues table and loads that into the first tab
        cur.execute("SELECT IssuesID from ProjectIssues WHERE ProjectID='" + str(loadedProjId) + "'")
        issuesList = cur.fetchall()
        issuesList = [x[0] for x in issuesList] #constantly being returned tuples is frustrating ....
        print(issuesList)
        #terrible way of using list to query incoming!
        placeholder= '?'
        placeholders = ', '.join(placeholder for unused in issuesList)
        query = 'SELECT * FROM Issues WHERE ID IN (%s)' % placeholders
        cur.execute(query, issuesList)
        issuesList = cur.fetchall() #may as well use again, variable is useless and name still functions
        self.issueTable.setRowCount(len(issuesList))
        for x in range(len(issuesList)):
            self.issueTable.setItem(x, 0, QTableWidgetItem(str(issuesList[x][1])))
            self.issueTable.setItem(x, 1, QTableWidgetItem(str(issuesList[x][2])))
            self.issueTable.setItem(x, 2, QTableWidgetItem(str(issuesList[x][3])))
            self.issueTable.setItem(x, 3, QTableWidgetItem(str(issuesList[x][4])))
        self.issueTable.resizeRowsToContents()
        #now does the schedules table, can just reuse the issueslist variable
        cur.execute("SELECT SchedulesID from ProjectSchedules WHERE ProjectID='" + str(loadedProjId) + "'")
        issuesList = cur.fetchall()
        issuesList = [x[0] for x in issuesList] #constantly being returned tuples is frustrating ....
        print(issuesList)
        #terrible way of using list to query incoming!
        placeholder= '?'
        placeholders = ', '.join(placeholder for unused in issuesList)
        query = 'SELECT * FROM Schedules WHERE ID IN (%s)' % placeholders
        cur.execute(query, issuesList)
        issuesList = cur.fetchall()
        self.scheduleTable.setRowCount(len(issuesList))
        for x in range(len(issuesList)):
            self.scheduleTable.setItem(x, 0, QTableWidgetItem(str(issuesList[x][1])))
            self.scheduleTable.setItem(x, 1, QTableWidgetItem(str(issuesList[x][2])))
            self.scheduleTable.setItem(x, 2, QTableWidgetItem(str(issuesList[x][3])))
            self.scheduleTable.setItem(x, 3, QTableWidgetItem(str(issuesList[x][4])))
        self.scheduleTable.resizeRowsToContents()

    def removeTask(self):
        issue = False
        error = QMessageBox()
        error.setIcon(QMessageBox.Critical)
        error.setWindowTitle("Error")
        if self.bugTab.currentIndex() == 0:
            issue = True
        if(issue == True and self.issueTable.currentRow() == -1):
            error.setText("Please select a row on the table by clicking in order to remove.")
            error.exec()
        elif(issue == False and self.scheduleTable.currentRow() == -1):
            error.setText("Please select a row on the table by clicking in order to remove.")
            error.exec()
        else: #actually deleting something if it reaches this else statement.
            sure = QMessageBox()
            sure.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            if issue:
                row = self.issueTable.currentRow()
                sure.setText("Are you sure you want to delete: '" +
                             self.issueTable.item(row, 0).text() + "'?")
            else:
                row = self.scheduleTable.currentRow()
                sure.setText("Are you sure you want to delete: '" +
                             self.scheduleTable.item(row, 0).text() + "'?")
            retval = sure.exec_()
            #retval = 1024 if the user presses OK
            if(retval == 1024):
                deletedValues = [0, 0, 0, 0]
                if issue:
                    table = "Issues"
                    for i in range(4):
                        deletedValues[i] = self.issueTable.item(row, i).text()
                        print(deletedValues)
                else:
                    table = "Schedules"
                    for i in range(4):
                        deletedValues[i] = self.scheduleTable.item(row, i).text()
                        print(deletedValues)
                conn = sqlite3.connect("bugtracker.db")
                cur = conn.cursor()
                cur.execute("SELECT ID FROM " + table +
                " WHERE Title='"+deletedValues[0] +
                "' AND Description='"+deletedValues[1] +
                "' AND Type='"+deletedValues[2] +
                "' AND Priority='" + deletedValues[3] + "'")
                data = cur.fetchone()
                cur.execute("DELETE FROM " + table +
                " WHERE ID='"+str(data[0])+"'")
                cur.execute("DELETE FROM Project"+table+
                " WHERE "+table+"ID='"+str(data[0])+"'")
                conn.commit()
                conn.close()
                self.fillTable()


def initialDBCheck():
    if(os.path.isfile(os.getcwd()+"/bugtracker.db") == False):
        con = sqlite3.connect('bugtracker.db') #this actually creates the file .. dont need shenanigans
        cur = con.cursor() #create table correctly if necessary
        cur.execute('''CREATE TABLE Projects (
        ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, 
        Name TEXT, 
        Description TEXT)''')
        cur.execute('''CREATE TABLE Issues (
        ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	    Title	TEXT,
	    Description	TEXT,
	    Type	TEXT,
	    Priority	TEXT)''')
        cur.execute('''CREATE TABLE ProjectIssues (
        ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        ProjectID INTEGER,
	    IssuesID INTEGER,
	    FOREIGN KEY(ProjectID) REFERENCES Projects(ID),
	    FOREIGN KEY(IssuesID) REFERENCES Issues(ID))''')
        cur.execute('''CREATE TABLE Schedules (
        ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
	    Title	TEXT,
	    Description	TEXT,
	    Type	TEXT,
	    Priority	TEXT)''')
        cur.execute('''CREATE TABLE ProjectSchedules (
        ID INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
        ProjectID INTEGER,
	    SchedulesID INTEGER,
	    FOREIGN KEY(ProjectID) REFERENCES Projects(ID),
	    FOREIGN KEY(SchedulesID) REFERENCES Schedules(ID))''')
        con.commit()
        con.close()

#initialise the app
def main():
    initialDBCheck()
    app = QApplication(sys.argv)
    UIWindow = ui()
    app.exec_()

#best practise
if __name__ == '__main__':
    main()