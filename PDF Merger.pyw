import os
import sys
import subprocess
from PyPDF2 import PdfFileMerger, PdfFileReader
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog
from PDFMergerUI import *


class App(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("PDF Merger")
        self.setWindowIcon(QtGui.QIcon('/usr/share/pixmaps/PDF Merger.png'))
        self.ui.OpenFile.setDisabled(True)
        self.ui.OpenFolder.setDisabled(True)
        self.ui.FolderSelector.setIcon(QtGui.QIcon("/usr/share/icons/Qogir-dark/128/places/default-folder.svg"))
        self.ui.FolderSelector.clicked.connect(self.browseDirectory)
        self.ui.Merger.setDisabled(True)
        self.ui.OutputBox.textChanged.connect(self.enableMergeButton)
        self.ui.Merger.clicked.connect(self.mergeDocs)
        self.ui.OpenFolder.clicked.connect(self.openFolder)
        self.ui.OpenFile.clicked.connect(self.openFile)
        self.ui.ClearFields.clicked.connect(self.clearFields)
        self.ui.progressBar.setValue(0)
        self.ui.Folder.textEdited.connect(self.checkPath)
    
    def enableMergeButton(self):
        if self.ui.OutputBox.text().endswith(".pdf") and self.ui.OpenFolder.isEnabled():
            self.ui.Merger.setEnabled(True)
        else:
            self.ui.Merger.setDisabled(True)
            
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
        
    def browseDirectory(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, options=options)
        self.ui.Folder.setText(directory)
        self.ui.Folder.textEdited.connect(self.checkPath)
        self.ui.OpenFolder.setEnabled(True)
    
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

