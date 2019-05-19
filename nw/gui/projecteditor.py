# -*- coding: utf-8 -*-
"""novelWriter GUI Project Editor

 novelWriter – GUI Project Editor
===================================
 Class holding the project editor

 File History:
 Created: 2018-09-29 [0.0.1]

"""

import logging
import nw

from os import path

from PyQt5.QtGui     import QIcon, QPixmap, QColor, QBrush
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (
    QDialog, QHBoxLayout, QVBoxLayout, QFormLayout, QLineEdit, QPlainTextEdit, QLabel,
    QWidget, QTabWidget, QDialogButtonBox, QListWidget, QListWidgetItem, QPushButton,
    QColorDialog
)
from nw.enum import nwAlert

logger = logging.getLogger(__name__)

class GuiProjectEditor(QDialog):

    def __init__(self, theParent, theProject):
        QDialog.__init__(self, theParent)

        logger.debug("Initialising ProjectEditor ...")

        self.mainConf   = nw.CONFIG
        self.theParent  = theParent
        self.theProject = theProject
        self.outerBox   = QHBoxLayout()
        self.innerBox   = QVBoxLayout()

        self.setWindowTitle("Project Settings")

        self.gradPath = path.abspath(path.join(self.mainConf.appPath,"graphics","block.svg"))
        self.svgGradient = QSvgWidget(self.gradPath)
        self.svgGradient.setFixedWidth(80)

        self.theProject.countStatus()
        self.tabMain   = GuiProjectEditMain(self.theParent, self.theProject)
        self.tabStatus = GuiProjectEditStatus(self.theParent, self.theProject.statusItems)
        self.tabImport = GuiProjectEditStatus(self.theParent, self.theProject.importItems)

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.tabMain,  "Settings")
        self.tabWidget.addTab(self.tabStatus,"Status")
        self.tabWidget.addTab(self.tabImport,"Importance")

        self.setLayout(self.outerBox)
        self.outerBox.addWidget(self.svgGradient)
        self.outerBox.addLayout(self.innerBox)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self._doSave)
        self.buttonBox.rejected.connect(self._doClose)

        self.innerBox.addWidget(self.tabWidget)
        self.innerBox.addWidget(self.buttonBox)

        self.show()

        logger.debug("ProjectEditor initialisation complete")

        return

    def _doSave(self):
        logger.verbose("ProjectEditor save button clicked")

        projName    = self.tabMain.editName.text()
        bookTitle   = self.tabMain.editTitle.text()
        bookAuthors = self.tabMain.editAuthors.toPlainText()
        self.theProject.setProjectName(projName)
        self.theProject.setBookTitle(bookTitle)
        self.theProject.setBookAuthors(bookAuthors)

        if self.tabStatus.colChanged:
            statusCol = self.tabStatus.getNewList()
            self.theProject.setStatusColours(statusCol)
        if self.tabImport.colChanged:
            importCol = self.tabImport.getNewList()
            self.theProject.setImportColours(importCol)
        if self.tabStatus.colChanged or self.tabImport.colChanged:
            self.theParent.rebuildTree()

        self.close()

        return

    def _doClose(self):
        logger.verbose("ProjectEditor close button clicked")
        self.close()
        return

# END Class GuiProjectEditor

class GuiProjectEditMain(QWidget):

    def __init__(self, theParent, theProject):
        QWidget.__init__(self, theParent)

        self.theParent   = theParent
        self.theProject  = theProject
        self.mainForm    = QFormLayout()
        self.editName    = QLineEdit()
        self.editTitle   = QLineEdit()
        self.editAuthors = QPlainTextEdit()

        self.mainForm.addRow("Working Title", self.editName)
        self.mainForm.addRow("Book Title",    self.editTitle)
        self.mainForm.addRow("Book Authors",  self.editAuthors)

        self.editName.setText(self.theProject.projName)
        self.editTitle.setText(self.theProject.bookTitle)
        bookAuthors = ""
        for bookAuthor in self.theProject.bookAuthors:
            bookAuthors += bookAuthor+"\n"
        self.editAuthors.setPlainText(bookAuthors)

        self.setLayout(self.mainForm)

        return

# END Class GuiProjectEditMain

class GuiProjectEditStatus(QWidget):

    def __init__(self, theParent, theStatus):
        QWidget.__init__(self, theParent)

        self.theParent  = theParent
        self.theStatus  = theStatus
        self.colNames   = []
        self.colCounts  = []
        self.colChanged = False

        self.mainBox    = QHBoxLayout()
        self.mainForm   = QVBoxLayout()

        self.listBox    = QListWidget()
        self.listBox.itemSelectionChanged.connect(self._selectedItem)

        for iName, iCol, nUse in self.theStatus:
            self._addItem("%s [%d]" % (iName, nUse), iCol)
            self.colNames.append(iName)
            self.colCounts.append(nUse)

        self.editName   = QLineEdit()
        self.newButton  = QPushButton("New")
        self.delButton  = QPushButton("Delete")
        self.saveButton = QPushButton("Save")
        self.colPixmap  = QPixmap(16,16)
        self.colPixmap.fill(QColor(120,120,120))
        self.colButton  = QPushButton(QIcon(self.colPixmap),"Colour")
        self.colButton.setIconSize(self.colPixmap.rect().size())

        self.newButton.clicked.connect(self._newItem)
        self.delButton.clicked.connect(self._delItem)
        self.saveButton.clicked.connect(self._saveItem)
        self.colButton.clicked.connect(self._selectColour)

        self.mainForm.addWidget(self.newButton)
        self.mainForm.addWidget(self.delButton)
        self.mainForm.addStretch(1)
        self.mainForm.addWidget(QLabel("<b>Name</b>"))
        self.mainForm.addWidget(self.editName)
        self.mainForm.addWidget(self.colButton)
        self.mainForm.addStretch(1)
        self.mainForm.addWidget(self.saveButton)

        self.mainBox.addWidget(self.listBox)
        self.mainBox.addLayout(self.mainForm)

        self.setLayout(self.mainBox)

        return

    def getNewList(self):
        if self.colChanged:
            newList = []
            for n in range(self.listBox.count()):
                nItem = self.listBox.item(n)
                nName = self._cleanLabel(nItem.text())
                nImg  = nItem.icon().pixmap(16,16).toImage()
                nCol  = QColor(nImg.pixel(7,7))
                newList.append((nName,nCol.red(),nCol.green(),nCol.blue(),self.colNames[n]))
            return newList
        return None

    ##
    #  User Actions
    ##

    def _selectColour(self):
        logger.verbose("Item colour button clicked")
        selImg = self.colButton.icon().pixmap(16,16).toImage()
        selCol = QColor(selImg.pixel(7,7))
        newCol = QColorDialog.getColor(selCol, self, "Select Colour", QColorDialog.DontUseNativeDialog)
        if newCol:
            colPixmap = QPixmap(16,16)
            colPixmap.fill(newCol)
            self.colButton.setIcon(QIcon(colPixmap))
            self.colButton.setIconSize(colPixmap.rect().size())
        return

    def _newItem(self):
        newItem = self._addItem("New Item [0]", (0, 0, 0))
        newItem.setBackground(QBrush(QColor(0,255,0,80)))
        self.colNames.append(None)
        self.colCounts.append(0)
        self.colChanged = True
        return

    def _delItem(self):
        selItem = self._getSelectedItem()
        iRow    = self.listBox.row(selItem)
        if self.colCounts[iRow] == 0:
            self.listBox.takeItem(iRow)
            self.colChanged = True
        else:
            self.theParent.makeAlert("Cannot delete status item that is in use.",nwAlert.ERROR)
        return

    def _saveItem(self):
        logger.verbose("Item save button clicked")
        selItem = self._getSelectedItem()
        iRow    = self.listBox.row(selItem)
        if selItem is not None:
            selItem.setText("%s [%d]" % (self.editName.text().strip(), self.colCounts[iRow]))
            selItem.setIcon(self.colButton.icon())
            self.colChanged = True
        return

    def _addItem(self, iName, iCol):
        logger.verbose("New item button clicked")
        newIcon = QPixmap(16,16)
        newIcon.fill(QColor(*iCol))
        newItem = QListWidgetItem()
        newItem.setText(iName)
        newItem.setIcon(QIcon(newIcon))
        self.listBox.addItem(newItem)
        return newItem

    def _selectedItem(self):
        logger.verbose("Item selected")
        selItem = self._getSelectedItem()
        if selItem is not None:
            self.editName.setText(self._cleanLabel(selItem.text()))
            self.colButton.setIcon(selItem.icon())
        return

    ##
    #  Internal Functions
    ##

    def _getSelectedItem(self):
        selItem = self.listBox.selectedItems()
        if len(selItem) == 0:
            return None
        if isinstance(selItem[0], QListWidgetItem):
            return selItem[0]
        return None

    def _cleanLabel(self, theText):
        iPos = theText.rfind("[")
        if iPos > 0:
            return theText[:iPos-1]
        else:
            return theText

# END Class GuiProjectEditStatus
