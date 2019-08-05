#!/usr/bin/python3

import os
import sys
import subprocess
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QMessageBox
from PDFMergerUI import *


class App(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("PDF Merger")
        self.setWindowIcon(QtGui.QIcon('/usr/share/pixmaps/PDF Merger.png'))
        self.ui.OpenFile.setDisabled(True)
        self.ui.OpenFile.clicked.connect(self.openFile)
        self.ui.OpenFolder.setDisabled(True)
        self.ui.OpenFolder.clicked.connect(self.openFolder)
        self.ui.FolderSelector.setIcon(QtGui.QIcon("/usr/share/icons/Qogir-dark/128/places/default-folder.svg"))
        self.ui.FolderSelector.clicked.connect(self.browseDirectory)
        self.ui.OK.clicked.connect(self.execute)
        self.ui.ClearFields.clicked.connect(self.clearFields)
        self.ui.progressBar.setValue(0)
        self.ui.Folder.textEdited.connect(self.checkPath)
        self.ui.README.clicked.connect(self.showInfo)
        self.ui.action.buttonClicked.connect(self.checkButton)
        self.show()

    def showInfo(self):
        file = os.path.abspath("README.md")
        if sys.platform == "win32":
            os.startfile(file)
        else:
            opener = "xdg-open" if sys.platform == "linux" else "open"
            subprocess.call([opener, file])
        
    def checkButton(self):
        if self.ui.filterPages.isChecked():
            self.ui.OutputBox.setDisabled(True)
        else:
            self.ui.OutputBox.setEnabled(True)
    def browseDirectory(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, options=options)
        self.ui.Folder.setText(directory)
        self.ui.Folder.textEdited.connect(self.checkPath)
        self.ui.OpenFolder.setEnabled(True)

    def enableOkButton(self):
        if (self.ui.action.checkedId() != -1) and (self.ui.OpenFolder.isEnabled()):
            self.ui.OK.setEnabled(True)

    def clearFields(self):
        self.ui.Folder.setText("")
        self.ui.OutputBox.setText("")
        self.ui.OpenFile.setDisabled(True)
        self.ui.OpenFolder.setDisabled(True)
        self.ui.progressBar.setValue(0)
        self.ui.DONE.setText("")
    
    def openFolder(self):
        folder = self.ui.Folder.text()
        if sys.platform == "win32":
            os.startfile(folder)
        else:
            opener = "xdg-open" if sys.platform == "linux" else "open"
            subprocess.call([opener, folder])
        
    def openFile(self):
        folder = self.ui.Folder.text()
        file = self.ui.OutputBox.text()
        if sys.platform == "win32":
            os.startfile(file)
        else:
            opener = "xdg-open" if sys.platform == "linux" else "open"
            subprocess.call([opener, os.path.join(folder, file)])
        

    def extractFirstPage(self, doc):
    
        try:
            os.mkdir("PDFs without first and last pages")
        except FileExistsError:
            pass
        finally:
            new_folder = "PDFs without first and last pages"
        
        inputpdf = PdfFileReader(open(doc,"rb"))
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(0))
        
        doc = os.path.join(os.path.abspath(new_folder), "Portada.pdf")
        with open(doc, "wb") as outputStream:
            output.write(outputStream)
        self.ui.progressBar.setValue(100)
        return doc


    def extractLastPage(self, doc):

        try:
            os.mkdir("PDFs without first and last pages")
        except FileExistsError:
                pass
        finally:
                new_folder = "PDFs without first and last pages"
        
        inputpdf = PdfFileReader(open(doc,"rb"))
        output = PdfFileWriter()
        output.addPage(inputpdf.getPage(inputpdf.numPages - 1))

        doc = os.path.join(os.path.abspath(new_folder), "Contraportada.pdf")
        with open(doc, "wb") as outputStream:
            output.write(outputStream)
        self.ui.progressBar.setValue(100)
        return doc

    
    def removeFirstLastPages(self, doc):
        
        try:
            os.mkdir("PDFs without first and last pages")
        except FileExistsError:
            pass
        finally:
            new_folder = "PDFs without first and last pages"
        
        inputpdf = PdfFileReader(open(doc,"rb"))
        output = PdfFileWriter()
        
        for i in range(1, inputpdf.numPages - 1):
            output.addPage(inputpdf.getPage(i))

        doc = os.path.basename(doc)
        doc = os.path.join(new_folder, doc)
        with open(doc, "wb") as outputStream:
            output.write(outputStream)
    

    def mergeDocs(self):
        folder = self.ui.Folder.text()
        new_file = self.ui.OutputBox.text()
        os.chdir(folder)
        pdfs = [pdf for pdf in sorted(os.listdir(os.getcwd()), key=os.path.getmtime) if pdf.endswith(".pdf")]
        completed = 0
        if pdfs:
            num_docs = len(pdfs)
            write_percentage = 100 - 10
            percentage = write_percentage / num_docs
            merger = PdfFileMerger()
            while pdfs:
                pdf = pdfs[0]
                with open(file=pdf, mode="rb") as file:
                    file = PdfFileReader(file)
                    merger.append(file)
                completed += percentage
                self.ui.progressBar.setValue(completed)
                pdfs.remove(pdf)
        merger.write(os.path.join(folder, new_file))
        self.ui.progressBar.setValue(100)
        self.ui.DONE.setText("DONE!")
        self.ui.OpenFile.setEnabled(True)

    def execute(self):
        if self.ui.action.checkedId() != -1 and self.ui.OpenFolder.isEnabled():
            os.chdir(self.ui.Folder.text())
            pdfs = [pdf for pdf in sorted(os.listdir(os.getcwd()), key=os.path.getmtime) if pdf.endswith(".pdf")]
            if self.ui.filterPages.isChecked():
                for pdf in pdfs:
                        self.removeFirstLastPages(doc=pdf)
            elif self.ui.frontCover.isChecked():
                self.extractFirstPage(doc=pdfs[0])
            elif self.ui.backCover.isChecked():
                self.extractLastPage(doc=pdfs[0])
            elif self.ui.mergePdfs.isChecked():
                self.mergeDocs()
        else:
            if self.ui.action.checkedId() == -1:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Warning")
                msg.setText("""You must first select an option.""")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Warning")
                msg.setText("""You must first select a folder.""")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()

    def checkPath(self):
        directory = self.ui.Folder.text()
        if os.path.exists(directory):
            self.ui.OpenFolder.setEnabled(True)
        else:
            self.ui.OpenFolder.setDisabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(w.exec_())
