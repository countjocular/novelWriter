# -*- coding: utf-8 -*-
"""novelWriter GUI Main Window

 novelWriter – GUI Main Window
===============================
 Class holding the main window

 File History:
 Created: 2018-09-22 [0.0.1]

"""

import logging
import time
import nw

from os import path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QColor, QKeySequence
from PyQt5.QtWidgets import (
    qApp, QMainWindow, QVBoxLayout, QFrame, QSplitter, QFileDialog, QShortcut,
    QMessageBox, QProgressDialog, QDialog
)

from nw.gui import (
    GuiMainMenu, GuiMainStatus, GuiTheme, GuiDocTree, GuiDocEditor, GuiExport,
    GuiDocViewer, GuiDocDetails, GuiSearchBar, GuiNoticeBar, GuiDocViewDetails,
    GuiConfigEditor, GuiProjectEditor, GuiItemEditor, GuiTimeLineView,
    GuiSessionLogView, GuiDocMerge, GuiDocSplit
)
from nw.project import NWProject, NWDoc, NWItem, NWIndex, NWBackup
from nw.tools import countWords
from nw.constants import nwFiles, nwItemType, nwAlert

logger = logging.getLogger(__name__)

class GuiMain(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        logger.info("Starting %s" % nw.__package__)
        logger.debug("Initialising GUI ...")
        self.mainConf   = nw.CONFIG
        self.theTheme   = GuiTheme(self)
        self.theProject = NWProject(self)
        self.theIndex   = NWIndex(self.theProject, self)
        self.hasProject = False
        self.isZenMode  = False

        logger.info("OS: %s" % (
            self.mainConf.osType)
        )
        logger.info("Qt5 Version: %s (%d)" % (
            self.mainConf.verQtString, self.mainConf.verQtValue)
        )
        logger.info("PyQt5 Version: %s (%d)" % (
            self.mainConf.verPyQtString, self.mainConf.verPyQtValue)
        )
        logger.info("Python Version: %s (0x%x)" % (
            self.mainConf.verPyString, self.mainConf.verPyHexVal)
        )

        self.resize(*self.mainConf.winGeometry)
        self._setWindowTitle()
        self.setWindowIcon(QIcon(path.join(self.mainConf.appIcon)))

        # Main GUI Elements
        self.statusBar = GuiMainStatus(self)
        self.noticeBar = GuiNoticeBar(self)
        self.docEditor = GuiDocEditor(self, self.theProject)
        self.docViewer = GuiDocViewer(self, self.theProject)
        self.viewMeta  = GuiDocViewDetails(self, self.theProject)
        self.searchBar = GuiSearchBar(self)
        self.treeMeta  = GuiDocDetails(self, self.theProject)
        self.treeView  = GuiDocTree(self, self.theProject)
        self.mainMenu  = GuiMainMenu(self, self.theProject)

        # Minor Gui Elements
        self.statusIcons = []
        self.importIcons = []

        # Assemble Main Window
        self.treePane = QFrame()
        self.treeBox = QVBoxLayout()
        self.treeBox.setContentsMargins(0,0,0,0)
        self.treeBox.addWidget(self.treeView)
        self.treeBox.addWidget(self.treeMeta)
        self.treePane.setLayout(self.treeBox)

        self.editPane = QFrame()
        self.docEdit = QVBoxLayout()
        self.docEdit.setContentsMargins(0,0,0,0)
        self.docEdit.addWidget(self.searchBar)
        self.docEdit.addWidget(self.noticeBar)
        self.docEdit.addWidget(self.docEditor)
        self.editPane.setLayout(self.docEdit)

        self.viewPane = QFrame()
        self.docView = QVBoxLayout()
        self.docView.setContentsMargins(0,0,0,0)
        self.docView.addWidget(self.docViewer)
        self.docView.addWidget(self.viewMeta)
        self.docView.setStretch(0, 1)
        self.viewPane.setLayout(self.docView)

        self.splitView = QSplitter(Qt.Horizontal)
        self.splitView.setOpaqueResize(False)
        self.splitView.addWidget(self.editPane)
        self.splitView.addWidget(self.viewPane)

        self.splitMain = QSplitter(Qt.Horizontal)
        self.splitMain.setContentsMargins(4,4,4,4)
        self.splitMain.setOpaqueResize(False)
        self.splitMain.addWidget(self.treePane)
        self.splitMain.addWidget(self.splitView)
        self.splitMain.setSizes(self.mainConf.mainPanePos)

        self.setCentralWidget(self.splitMain)

        self.idxTree   = self.splitMain.indexOf(self.treePane)
        self.idxMain   = self.splitMain.indexOf(self.splitView)
        self.idxEditor = self.splitView.indexOf(self.editPane)
        self.idxViewer = self.splitView.indexOf(self.viewPane)

        self.splitMain.setCollapsible(self.idxTree, False)
        self.splitMain.setCollapsible(self.idxMain, False)
        self.splitView.setCollapsible(self.idxEditor, False)
        self.splitView.setCollapsible(self.idxViewer, True)

        self.viewPane.setVisible(False)
        self.searchBar.setVisible(False)

        # Build The Tree View
        self.treeView.itemSelectionChanged.connect(self._treeSingleClick)
        self.treeView.itemDoubleClicked.connect(self._treeDoubleClick)
        self.rebuildTree()

        # Set Main Window Elements
        self.setMenuBar(self.mainMenu)
        self.setStatusBar(self.statusBar)
        self.statusBar.setStatus("Ready")

        # Set Up Autosaving Project Timer
        self.asProjTimer = QTimer()
        self.asProjTimer.timeout.connect(self._autoSaveProject)

        # Set Up Autosaving Document Timer
        self.asDocTimer = QTimer()
        self.asDocTimer.timeout.connect(self._autoSaveDocument)

        # Shortcuts and Actions
        self._connectMenuActions()
        keyReturn = QShortcut(self.treeView)
        keyReturn.setKey(QKeySequence(Qt.Key_Return))
        keyReturn.activated.connect(self._treeKeyPressReturn)
        keyEscape = QShortcut(self)
        keyEscape.setKey(QKeySequence(Qt.Key_Escape))
        keyEscape.activated.connect(self._keyPressEscape)

        # Forward Functions
        self.setStatus = self.statusBar.setStatus
        self.setProjectStatus = self.statusBar.setProjectStatus

        if self.mainConf.showGUI:
            self.show()

        self.initMain()
        self.asProjTimer.start()
        self.asDocTimer.start()
        self.statusBar.clearStatus()

        self.showNormal()
        if self.mainConf.isFullScreen:
            self.toggleFullScreenMode()

        logger.debug("GUI initialisation complete")

        if self.mainConf.cmdOpen is not None:
            logger.debug("Opening project from additional command line option")
            self.openProject(self.mainConf.cmdOpen)

        return

    def clearGUI(self):
        """Wrapper function to clear all sub-elements of the main GUI.
        """
        self.treeView.clearTree()
        self.docEditor.clearEditor()
        self.closeDocViewer()
        self.statusBar.clearStatus()
        return True

    def initMain(self):
        self.asProjTimer.setInterval(int(self.mainConf.autoSaveProj*1000))
        self.asDocTimer.setInterval(int(self.mainConf.autoSaveDoc*1000))
        return True

    ##
    #  Project Actions
    ##

    def newProject(self, projPath=None, forceNew=False):

        if self.hasProject:
            msgBox = QMessageBox()
            msgRes = msgBox.warning(
                self, "New Project",
                "Please close the current project<br>before making a new one."
            )
            return False

        if projPath is None:
            projPath = self.newProjectDialog()
        if projPath is None:
            return False

        if path.isfile(path.join(projPath,self.theProject.projFile)) and not forceNew:
            msgBox = QMessageBox()
            msgRes = msgBox.critical(
                self, "New Project",
                "A project already exists in that location.<br>Please choose another folder."
            )
            return False

        logger.info("Creating new project")
        self.theProject.newProject()
        self.theProject.setProjectPath(projPath)
        self.rebuildTree()
        self.saveProject()
        self.hasProject = True
        self.statusBar.setRefTime(self.theProject.projOpened)

        return True

    def closeProject(self, isYes=False):
        """Closes the project if one is open.
        isYes is passed on from the close application event so the user
        doesn't get prompted twice.
        """
        if not self.hasProject:
            # There is no project loaded, everything OK
            return True

        if self.mainConf.showGUI and not isYes:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self, "Close Project", "Save changes and close current project?"
            )
            if msgRes != QMessageBox.Yes:
                return False

        if self.docEditor.docChanged:
            self.saveDocument()

        if self.theProject.projAltered:
            saveOK   = self.saveProject()
            doBackup = False
            if self.theProject.doBackup and self.mainConf.backupOnClose:
                doBackup = True
                if self.mainConf.showGUI and self.mainConf.askBeforeBackup:
                    msgBox = QMessageBox()
                    msgRes = msgBox.question(
                        self, "Backup Project", "Backup current project?"
                    )
                    if msgRes != QMessageBox.Yes:
                        doBackup = False
            if doBackup:
                self.backupProject()
        else:
            saveOK = True

        if saveOK:
            self.closeDocument()
            self.theProject.closeProject()
            self.theIndex.clearIndex()
            self.clearGUI()
            self.hasProject = False

        return saveOK

    def openProject(self, projFile=None):
        """Open a project. The parameter projFile is passed from the
        open recent projects menu, so it can be set. If not, we pop the
        dialog.
        """
        if projFile is None:
            projFile = self.openProjectDialog()
        if projFile is None:
            return False

        # Make sure any open project is cleared out first before we load
        # another one
        if not self.closeProject():
            return False

        # Try to open the project
        if not self.theProject.openProject(projFile):
            return False

        # project is loaded
        self.hasProject = True

        # Load the tag index
        self.theIndex.loadIndex()

        # Update GUI
        self._setWindowTitle(self.theProject.projName)
        self.rebuildTree()
        self.docEditor.setDictionaries()
        self.docEditor.setSpellCheck(self.theProject.spellCheck)
        self.statusBar.setRefTime(self.theProject.projOpened)
        self.mainMenu.updateMenu()

        # Restore previously open documents, if any
        if self.theProject.lastEdited is not None:
            self.openDocument(self.theProject.lastEdited)
        if self.theProject.lastViewed is not None:
            self.viewDocument(self.theProject.lastViewed)

        # Check if we need to rebuild the index
        if self.theIndex.indexBroken:
            self.rebuildIndex()

        return True

    def saveProject(self):
        """Save the current project.
        """
        if not self.hasProject:
            return False

        # If the project is new, it may not have a path, so we need one
        if self.theProject.projPath is None:
            projPath = self.saveProjectDialog()
            self.theProject.setProjectPath(projPath)
        if self.theProject.projPath is None:
            return False

        self.treeView.saveTreeOrder()
        self.theProject.saveProject()
        self.theIndex.saveIndex()
        self.mainMenu.updateRecentProjects()

        return True

    def backupProject(self):
        theBackup = NWBackup(self, self.theProject)
        theBackup.zipIt()
        return True

    ##
    #  Document Actions
    ##

    def closeDocument(self):
        if self.hasProject:
            if self.docEditor.docChanged:
                self.saveDocument()
            self.docEditor.clearEditor()
        return True

    def openDocument(self, tHandle):
        if self.hasProject:
            self.closeDocument()
            if self.docEditor.loadText(tHandle):
                self.docEditor.setFocus()
                self.theProject.setLastEdited(tHandle)
            else:
                return False
        return True

    def saveDocument(self):
        if self.hasProject:
            self.docEditor.saveText()
        return True

    def viewDocument(self, tHandle=None):

        if tHandle is None:
            tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.debug("No document selected, trying editor document")
            tHandle = self.docEditor.theHandle
        if tHandle is None:
            logger.debug("No document selected, trying last viewed")
            tHandle = self.theProject.lastViewed
        if tHandle is None:
            logger.debug("No document selected, giving up")
            return False

        if self.docViewer.loadText(tHandle) and not self.viewPane.isVisible():
            bPos = self.splitMain.sizes()
            self.viewPane.setVisible(True)
            vPos = [0,0]
            vPos[0] = int(bPos[1]/2)
            vPos[1] = bPos[1]-vPos[0]
            self.splitView.setSizes(vPos)

        return True

    def importDocument(self):

        lastPath = self.mainConf.lastPath

        extFilter = [
            "Text files (*.txt)",
            "Markdown files (*.md)",
            "All files (*.*)",
        ]
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        inPath  = QFileDialog.getOpenFileName(
            self,"Import File",lastPath,options=dlgOpt,filter=";;".join(extFilter)
        )
        if inPath:
            loadFile = inPath[0]
        else:
            return False

        if loadFile.strip() == "":
            return False

        theText = None
        try:
            with open(loadFile,mode="rt",encoding="utf8") as inFile:
                theText = inFile.read()
            self.mainConf.setLastPath(loadFile)
        except Exception as e:
            self.makeAlert(
                ["Could not read file. The file must be an existing text file.",str(e)],
                nwAlert.ERROR
            )
            return False

        if self.docEditor.theHandle is None:
            self.makeAlert(
                ["Please open a document to import the text file into."],
                nwAlert.ERROR
            )
            return False

        if not self.docEditor.isEmpty():
            if self.mainConf.showGUI:
                msgBox = QMessageBox()
                msgRes = msgBox.question(self, "Import Document",(
                    "Importing the file will overwrite the current content of the document. "
                    "Do you want to proceed?"
                ))
                if msgRes != QMessageBox.Yes:
                    return False
            else:
                return False

        self.docEditor.replaceText(theText)

        return True

    def mergeDocuments(self):
        """Merge multiple documents to one single new document.
        """
        if self.mainConf.showGUI:
            dlgMerge = GuiDocMerge(self, self.theProject)
            dlgMerge.exec_()
        return True

    def splitDocument(self):
        """Split a single document into multiple documents.
        """
        if self.mainConf.showGUI:
            dlgSplit = GuiDocSplit(self, self.theProject)
            dlgSplit.exec_()
        return True

    def passDocumentAction(self, theAction):
        """Pass on document action theAction to whatever document has
        the focus. If no document has focus, the action is discarded.
        """
        if self.docEditor.hasFocus():
            self.docEditor.docAction(theAction)
        elif self.docViewer.hasFocus():
            self.docViewer.docAction(theAction)
        else:
            logger.debug("Document action requested, but no document has focus")
        return True

    ##
    #  Tree Item Actions
    ##

    def openSelectedItem(self):
        tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No item selected")
            return False

        logger.verbose("Opening item %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is not a file" % tHandle)

        return True

    def editItem(self):
        tHandle = self.treeView.getSelectedHandle()
        if tHandle is None:
            logger.warning("No item selected")
            return

        logger.verbose("Requesting change to item %s" % tHandle)
        if self.mainConf.showGUI:
            dlgProj = GuiItemEditor(self, self.theProject, tHandle)
            if dlgProj.exec_():
                self.treeView.setTreeItemValues(tHandle)

        return

    def rebuildTree(self):
        self._makeStatusIcons()
        self._makeImportIcons()
        self.treeView.clearTree()
        self.treeView.buildTree()
        return

    def rebuildIndex(self):

        if not self.hasProject:
            return False

        logger.debug("Rebuilding indices ...")

        self.treeView.saveTreeOrder()
        self.theIndex.clearIndex()
        nItems = len(self.theProject.treeOrder)

        dlgProg = QProgressDialog("Scanning files ...", "Cancel", 0, nItems, self)
        dlgProg.setWindowModality(Qt.WindowModal)
        dlgProg.setMinimumDuration(0)
        dlgProg.setFixedWidth(480)
        dlgProg.setLabelText("Starting file scan ...")
        dlgProg.setValue(0)
        dlgProg.show()
        time.sleep(0.5)

        nDone = 0
        for tHandle in self.theProject.treeOrder:

            tItem = self.theProject.getItem(tHandle)

            dlgProg.setValue(nDone)
            dlgProg.setLabelText("Scanning: %s" % tItem.itemName)
            logger.verbose("Scanning: %s" % tItem.itemName)

            if tItem is not None and tItem.itemType == nwItemType.FILE:
                theDoc  = NWDoc(self.theProject, self)
                theText = theDoc.openDocument(tHandle, False)

                # Run Word Count
                cC, wC, pC = countWords(theText)
                tItem.setCharCount(cC)
                tItem.setWordCount(wC)
                tItem.setParaCount(pC)
                self.treeView.propagateCount(tHandle, wC)
                self.treeView.projectWordCount()

                # Build tag index
                self.theIndex.scanText(tHandle, theText)

            nDone += 1
            if dlgProg.wasCanceled():
                break

        dlgProg.setValue(nItems)

        return True

    ##
    #  Main Dialogs
    ##

    def openProjectDialog(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projFile, _ = QFileDialog.getOpenFileName(
            self, "Open novelWriter Project", "",
            "novelWriter Project File (%s);;All Files (*)" % nwFiles.PROJ_FILE,
            options=dlgOpt
        )
        if projFile:
            return projFile
        return None

    def saveProjectDialog(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath = QFileDialog.getExistingDirectory(
            self, "Save novelWriter Project", "", options=dlgOpt
        )
        if projPath:
            return projPath
        return None

    def newProjectDialog(self):
        dlgOpt  = QFileDialog.Options()
        dlgOpt |= QFileDialog.ShowDirsOnly
        dlgOpt |= QFileDialog.DontUseNativeDialog
        projPath = QFileDialog.getExistingDirectory(
            self, "Select Location for New novelWriter Project", "", options=dlgOpt
        )
        if projPath:
            return projPath
        return None

    def editConfigDialog(self):
        dlgConf = GuiConfigEditor(self, self.theProject)
        if dlgConf.exec_() == QDialog.Accepted:
            logger.debug("Applying new preferences")
            self.initMain()
            self.theTheme.updateTheme()
            self.saveDocument()
            self.docEditor.initEditor()
            self.docViewer.initViewer()
        return True

    def editProjectDialog(self):
        if self.hasProject:
            dlgProj = GuiProjectEditor(self, self.theProject)
            dlgProj.exec_()
            self._setWindowTitle(self.theProject.projName)
        return True

    def exportProjectDialog(self):
        if self.hasProject:
            dlgExport = GuiExport(self, self.theProject)
            dlgExport.exec_()
        return True

    def showTimeLineDialog(self):
        if self.hasProject:
            dlgTLine = GuiTimeLineView(self, self.theProject, self.theIndex)
            dlgTLine.exec_()
        return True

    def showSessionLogDialog(self):
        if self.hasProject:
            dlgTLine = GuiSessionLogView(self, self.theProject)
            dlgTLine.exec_()
        return True

    def makeAlert(self, theMessage, theLevel=nwAlert.INFO):
        """Alert both the user and the logger at the same time. Message
        can be either a string or an array of strings. Severity level is
        0 = info, 1 = warning, and 2 = error.
        """

        if isinstance(theMessage, list):
            popMsg = " ".join(theMessage)
            logMsg = theMessage
        else:
            popMsg = theMessage
            logMsg = [theMessage]

        msgBox = QMessageBox()
        if theLevel == nwAlert.INFO:
            for msgLine in logMsg:
                logger.info(msgLine)
            msgBox.information(self, "Information", popMsg)
        elif theLevel == nwAlert.WARN:
            for msgLine in logMsg:
                logger.warning(msgLine)
            msgBox.warning(self, "Warning", popMsg)
        elif theLevel == nwAlert.ERROR:
            for msgLine in logMsg:
                logger.error(msgLine)
            msgBox.critical(self, "Error", popMsg)
        elif theLevel == nwAlert.BUG:
            for msgLine in logMsg:
                logger.error(msgLine)
            popMsg += "<br>This is a bug!"
            msgBox.critical(self, "Internal Error", popMsg)

        return

    ##
    #  Main Window Actions
    ##

    def closeMain(self):

        if self.mainConf.showGUI and self.hasProject:
            msgBox = QMessageBox()
            msgRes = msgBox.question(
                self, "Exit", "Do you want to save changes and exit?"
            )
            if msgRes != QMessageBox.Yes:
                return False

        logger.info("Exiting %s" % nw.__package__)
        self.closeProject(True)

        self.mainConf.setTreeColWidths(self.treeView.getColumnSizes())
        if not self.mainConf.isFullScreen:
            self.mainConf.setWinSize(self.width(), self.height())
        if not self.isZenMode:
            self.mainConf.setMainPanePos(self.splitMain.sizes())
            self.mainConf.setDocPanePos(self.splitView.sizes())
        self.mainConf.saveConfig()

        qApp.quit()

        return True

    def setFocus(self, paneNo):
        if paneNo == 1:
            self.treeView.setFocus()
        elif paneNo == 2:
            self.docEditor.setFocus()
        elif paneNo == 3:
            self.docViewer.setFocus()
        return

    def closeDocEditor(self):
        self.closeDocument()
        self.theProject.setLastEdited(None)
        return

    def closeDocViewer(self):
        self.docViewer.clearViewer()
        self.theProject.setLastViewed(None)
        bPos = self.splitMain.sizes()
        self.viewPane.setVisible(False)
        vPos = [bPos[1],0]
        self.splitView.setSizes(vPos)
        return not self.viewPane.isVisible()

    def toggleZenMode(self):
        """Main GUI Zen Mode hides tree, view pane and optionally also
        statusbar and menu.
        """

        if self.docEditor.theHandle is None:
            logger.error("No document open, so not activating Zen Mode")
            return False

        self.isZenMode = not self.isZenMode
        if self.isZenMode:
            logger.debug("Activating Zen mode")
        else:
            logger.debug("Deactivating Zen mode")

        isVisible = not self.isZenMode
        self.treePane.setVisible(isVisible)
        self.statusBar.setVisible(isVisible)
        self.mainMenu.setVisible(isVisible)

        if self.viewPane.isVisible():
            self.viewPane.setVisible(False)
        elif self.docViewer.theHandle is not None:
            self.viewPane.setVisible(True)

        return True

    def toggleFullScreenMode(self):
        """Main GUI full screen mode. The mode is tracked by the flag
        in config. This only tracks whether the window has been
        maximised using the internal commands, and may not be correct
        if the user uses the system window manager. Currently, Qt
        doesn't have access to the exact state of the window.
        """

        self.setWindowState(self.windowState() ^ Qt.WindowFullScreen)

        winState = self.windowState() & Qt.WindowFullScreen == Qt.WindowFullScreen
        if winState:
            logger.debug("Activated full screen mode")
        else:
            logger.debug("Deactivated full screen mode")

        self.mainConf.isFullScreen = winState

        return

    ##
    #  Internal Functions
    ##

    def _connectMenuActions(self):
        """Connect to the main window all menu actions that need to be
        available also when the main menu is hidden.
        """
        self.addAction(self.mainMenu.aSaveProject)
        self.addAction(self.mainMenu.aExitNW)
        self.addAction(self.mainMenu.aSaveDoc)
        self.addAction(self.mainMenu.aFileDetails)
        self.addAction(self.mainMenu.aZenMode)
        self.addAction(self.mainMenu.aFullScreen)
        self.addAction(self.mainMenu.aViewTimeLine)
        self.addAction(self.mainMenu.aEditUndo)
        self.addAction(self.mainMenu.aEditRedo)
        self.addAction(self.mainMenu.aEditCut)
        self.addAction(self.mainMenu.aEditCopy)
        self.addAction(self.mainMenu.aEditPaste)
        self.addAction(self.mainMenu.aSelectAll)
        self.addAction(self.mainMenu.aSelectPar)
        self.addAction(self.mainMenu.aFmtBold)
        self.addAction(self.mainMenu.aFmtItalic)
        self.addAction(self.mainMenu.aFmtULine)
        self.addAction(self.mainMenu.aFmtDQuote)
        self.addAction(self.mainMenu.aFmtSQuote)
        self.addAction(self.mainMenu.aFmtHead1)
        self.addAction(self.mainMenu.aFmtHead2)
        self.addAction(self.mainMenu.aFmtHead3)
        self.addAction(self.mainMenu.aFmtHead4)
        self.addAction(self.mainMenu.aFmtComment)
        self.addAction(self.mainMenu.aFmtNoFormat)
        self.addAction(self.mainMenu.aSpellCheck)
        self.addAction(self.mainMenu.aReRunSpell)
        self.addAction(self.mainMenu.aPreferences)
        self.addAction(self.mainMenu.aHelp)
        return True

    def _setWindowTitle(self, projName=None):
        winTitle = "%s" % nw.__package__
        if projName is not None:
            winTitle += " - %s" % projName
        self.setWindowTitle(winTitle)
        return True

    def _autoSaveProject(self):
        if (self.hasProject and self.theProject.projChanged and
            self.theProject.projPath is not None):
            logger.debug("Autosaving project")
            self.saveProject()
        return

    def _autoSaveDocument(self):
        if self.hasProject and self.docEditor.docChanged:
            logger.debug("Autosaving document")
            self.saveDocument()
        return

    def _makeStatusIcons(self):
        self.statusIcons = {}
        for sLabel, sCol, _ in self.theProject.statusItems:
            theIcon = QPixmap(32,32)
            theIcon.fill(QColor(*sCol))
            self.statusIcons[sLabel] = QIcon(theIcon)
        return

    def _makeImportIcons(self):
        self.importIcons = {}
        for sLabel, sCol, _ in self.theProject.importItems:
            theIcon = QPixmap(32,32)
            theIcon.fill(QColor(*sCol))
            self.importIcons[sLabel] = QIcon(theIcon)
        return

    ##
    #  Events
    ##

    def closeEvent(self, theEvent):
        if self.closeMain():
            theEvent.accept()
        else:
            theEvent.ignore()
        return

    ##
    #  Signal Handlers
    ##

    def _treeSingleClick(self):
        sHandle = self.treeView.getSelectedHandle()
        if sHandle is not None:
            self.treeMeta.buildViewBox(sHandle)
        return

    def _treeDoubleClick(self, tItem, colNo):
        tHandle = tItem.text(3)
        logger.verbose("User double clicked tree item with handle %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is a folder" % tHandle)
        return

    def _treeKeyPressReturn(self):
        tHandle = self.treeView.getSelectedHandle()
        logger.verbose("User pressed return on tree item with handle %s" % tHandle)
        nwItem = self.theProject.getItem(tHandle)
        if nwItem.itemType == nwItemType.FILE:
            logger.verbose("Requested item %s is a file" % tHandle)
            self.openDocument(tHandle)
        else:
            logger.verbose("Requested item %s is a folder" % tHandle)
        return

    def _keyPressEscape(self):
        """When the escape key is pressed somewhere in the main window,
        do the following, in order.
        """
        if self.searchBar.isVisible():
            self.searchBar.setVisible(False)
            return
        elif self.isZenMode:
            self.toggleZenMode()
        return

# END Class GuiMain
