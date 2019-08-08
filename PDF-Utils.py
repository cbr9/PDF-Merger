import os
import subprocess
import sys
from typing import List, Union

# noinspection PyProtectedMember
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QMainWindow, QMessageBox

from UserInterface import *


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("PDF Utils")
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.ui.openFile.clicked.connect(self.open_file)
        self.ui.rangePages.setDisabled(True)
        self.ui.extractPages.setDisabled(True)
        self.ui.extractPages.toggled.connect(self.ui.rangePages.setEnabled)
        self.ui.openFile.setDisabled(True)
        self.ui.mergeDocs.setDisabled(True)
        self.ui.clearFields.setDisabled(True)
        self.ui.clearFields.clicked.connect(self.clear_fields)
        self.listDocs = QDialog(self)
        self.docsLayout = QtWidgets.QVBoxLayout(self.listDocs)
        self.ui.editListOfDocs.clicked.connect(self.edit_selection)
        self.ui.editListOfDocs.clicked.connect(self.check_remove_button)
        self.remove = QtWidgets.QPushButton(text="Remove")
        self.add = QtWidgets.QPushButton(text="Add")
        self.buttonsLayout = QtWidgets.QHBoxLayout()
        self.buttonsLayout.addWidget(self.remove)
        self.buttonsLayout.addWidget(self.add)
        self.sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Expanding)
        self.add.setSizePolicy(self.sizePolicy)
        self.add.setMinimumSize(350, 50)
        self.add.setMaximumSize(13000000, 50)
        self.remove.setSizePolicy(self.sizePolicy)
        self.remove.setMinimumSize(350, 50)
        self.remove.setMaximumSize(13000000, 50)
        self.remove.clicked.connect(self.remove_documents)
        self.remove.clicked.connect(self.check_remove_button)
        self.docsLayout.addLayout(self.buttonsLayout)
        self.add.clicked.connect(self.add_documents)
        self.ui.OK.clicked.connect(self.execute)
        self.show()

    def edit_selection(self):
        self.listDocs.show()

    # noinspection PyAttributeOutsideInit
    def update_pdf_list(self):
        if not hasattr(self, "pdfs"):
            setattr(self, "pdfs", [widget for widget in self.subwidgets(self.docsLayout)
                                   if isinstance(widget, QtWidgets.QCheckBox)])
            setattr(self, "pdfs_text", [widget.text() for widget in self.pdfs])
        else:
            self.pdfs = [widget for widget in self.subwidgets(self.docsLayout) if isinstance(widget, QtWidgets.QCheckBox)]
            self.pdfs_text = [widget.text() for widget in self.pdfs]

    def enable_radios(self, pdfs: List):
        if len(pdfs) >= 1:
            if len(pdfs) == 1:
                self.ui.extractPages.setEnabled(True)
                self.ui.rangePages.setEnabled(True)
                self.ui.mergeDocs.setDisabled(True)
            elif len(pdfs) > 1:
                self.ui.mergeDocs.setEnabled(True)
                self.ui.extractPages.setDisabled(True)
                self.ui.rangePages.setDisabled(True)
        else:
            self.ui.mergeDocs.setDisabled(True)
            self.ui.extractPages.setDisabled(True)
            self.ui.rangePages.setDisabled(True)

    def add_documents(self):
        self.update_pdf_list()
        additions = QFileDialog.getOpenFileNames(self, caption="Select PDF documents", filter='PDF Files (*.pdf)')[0]
        for index, doc in enumerate(additions):
            if doc not in self.pdfs_text:
                checkbox = QtWidgets.QCheckBox(doc)
                checkbox.setText(doc)
                self.pdfs.append(checkbox)
                self.docsLayout.addWidget(checkbox, index)
        self.remove.setEnabled(True)
        self.enable_radios(pdfs=self.pdfs)
        self.update_pdf_list()

    @staticmethod
    def subwidgets(layout: Union[QtWidgets.QHBoxLayout, QtWidgets.QVBoxLayout, QtWidgets.QGridLayout]):
        widgets = (layout.itemAt(i).widget() for i in range(layout.count()))
        return widgets

    def check_remove_button(self):
        if hasattr(self, "pdfs"):
            if len(self.pdfs) != 0:
                self.remove.setEnabled(True)
            else:
                self.remove.setDisabled(True)

    def remove_documents(self):
        self.update_pdf_list()
        for widget in self.subwidgets(self.docsLayout):
            if isinstance(widget, QtWidgets.QCheckBox):
                if widget.isChecked():
                    widget.deleteLater()
                    self.pdfs.remove(widget)
                    self.listDocs.resize(250, self.listDocs.minimumHeight())
        self.check_remove_button()
        self.enable_radios(pdfs=self.pdfs)
        self.update_pdf_list()

    def clear_fields(self):
        self.ui.openFile.setDisabled(True)
        self.ui.outputName.clear()
        for widget in self.subwidgets(self.docsLayout):
            if isinstance(widget, QtWidgets.QCheckBox):
                widget.deleteLater()
                self.pdfs.remove(widget)
        self.update_pdf_list()

    def merge_docs(self, pdfs: List):
        new_file = self.ui.outputName.text()
        merger = PdfFileMerger()
        if pdfs:
            while pdfs:
                pdf = pdfs[0]
                with open(file=pdf, mode="rb") as file:
                    file = PdfFileReader(file)
                    merger.append(file)
                pdfs.remove(pdf)
        merger.write(new_file)
        self.ui.openFile.setEnabled(True)

    def execute(self):
        if os.path.exists(self.ui.outputName.text()):
            if self.overwrite():
                self.merge_docs(pdfs=self.pdfs_text)
            else:
                pass
        else:
            self.merge_docs(pdfs=self.pdfs_text)

    # noinspection PyUnresolvedReferences
    def open_file(self):
        folder = os.getcwd()
        file = os.path.join(folder, self.ui.outputName.text())
        if sys.platform == "win32":
            os.startfile(file)
        else:
            opener = "xdg-open" if sys.platform == "linux" else "open"
            subprocess.call([opener, file])

    @staticmethod
    def overwrite():
        warning = QMessageBox()
        warning.setIcon(QMessageBox.Question)
        warning.setText("The file name you have selected already exists. Do you wish to overwrite?")
        warning.setWindowTitle("Path exists.")
        warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        choice = warning.exec_()
        yes, no = 16384, 65536
        if choice == yes:
            return True
        elif choice == no:
            return False

    def extract_pages(self, doc: str):
        new_folder = ".temp"
        try:
            os.mkdir(new_folder)
        except FileExistsError:
            pass

        range_ = self.ui.rangePages.text().split("-")
        from_ = range_[0]
        to_ = range_[1] if len(range_) == 2 else (from_ + 1)
        every_ = range_[2] if len(range_) == 3 else 1
        input_pdf = PdfFileReader(open(file=doc, mode="rb"))
        output = PdfFileWriter()
        for page in input_pdf.numPages[from_:to_:every_]:
            output.addPage(input_pdf.getPage(page))

        with open("test.pdf", "wb") as outputStream:
            output.write(outputStream)
        # os.remove(new_folder)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec_())
