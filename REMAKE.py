import shutil
import os
import sys
import subprocess
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QMainWindow
from PyQt5.QtCore import *
from remakeUI import *


class App(QMainWindow):
	def __init__(self):
		super().__init__()
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.setWindowTitle("PDF Utils")
		self.setWindowIcon(QtGui.QIcon('/usr/share/pixmaps/PDF Merger.png'))
		self.ui.openFile.clicked.connect(self.openFile)
		self.ui.rangePages.setDisabled(True)
		self.ui.extractPages.setDisabled(True)
		self.ui.extractPages.toggled.connect(self.ui.rangePages.setEnabled)
		self.ui.openFile.setDisabled(True)
		self.ui.editListOfDocs.setDisabled(True)
		self.ui.mergeDocs.setDisabled(True)
		self.ui.clearFields.clicked.connect(self.clearFields)
		self.ui.selectDocs.clicked.connect(self.selectDocuments)
		self.listDocs = QDialog(self)
		self.docsLayout = QtWidgets.QVBoxLayout(self.listDocs)
		self.ui.editListOfDocs.clicked.connect(self.editSelection)
		self.remove = QtWidgets.QPushButton(text="Remove")
		self.add = QtWidgets.QPushButton(text="Add")
		self.buttonsLayout = QtWidgets.QHBoxLayout()
		self.buttonsLayout.addWidget(self.remove)
		self.buttonsLayout.addWidget(self.add)
		self.buttonsLayout.setAlignment(Qt.AlignBottom)
		self.docsLayout.addLayout(self.buttonsLayout)
		self.add.clicked.connect(self.addDocuments)
		self.remove.clicked.connect(self.removeDocuments)
		# self.ui.outputName.textChanged.connect(self.checkOutputPath)
		self.show()

	def editSelection(self):
		self.listDocs.show()

	def selectDocuments(self):
		pdfs = QFileDialog.getOpenFileNames(self, caption="Select PDF documents", filter='PDF Files (*.pdf)')
		pdfs = [pdf for pdf in pdfs][0]
		for index, doc in enumerate(pdfs):
			checkbox = QtWidgets.QCheckBox(doc)
			checkbox.setText(doc)
			self.docsLayout.addWidget(checkbox)
			self.docsLayout.setAlignment(Qt.AlignLeft)
		if pdfs:
			self.ui.editListOfDocs.setEnabled(True)
		if len(pdfs) == 1:
			self.ui.extractPages.setEnabled(True)
			self.ui.mergeDocs.setDisabled(True)
		else:
			self.ui.mergeDocs.setEnabled(True)
			self.ui.extractPages.setDisabled(True)
			self.ui.rangePages.setDisabled(True)

	def addDocuments(self):
		additions = QFileDialog.getOpenFileNames(self, caption="Select PDF documents", filter='PDF Files (*.pdf)')
		additions = [pdf for pdf in additions][0]
		for index, doc in enumerate(additions):
			checkbox = QtWidgets.QCheckBox(doc)
			checkbox.setText(doc)
			self.docsLayout.addWidget(checkbox)
			self.docsLayout.setAlignment(Qt.AlignLeft)

	@staticmethod
	def subWidgets(layout):
		widgets = (layout.itemAt(i).widget() for i in range(layout.count()))
		return widgets

	def removeDocuments(self):
		for widget in self.subWidgets(layout=self.docsLayout):
			if isinstance(widget, QtWidgets.QCheckBox):
				if widget.isChecked():
					self.docsLayout.removeWidget(widget)

	def clearFields(self):
		self.ui.openFile.setDisabled(True)
		self.ui.outputName.clear()

	def mergeDocs(self):
		## TAKE THE PDFS VARIABLE FROM THE WIDGETS IN SELF.DOCSLAYOUT ##
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

	def openFile(self):
		file = self.ui.outputName.text()
		if sys.platform == "win32":
			os.startfile(file)
		else:
			opener = "xdg-open" if sys.platform == "linux" else "open"
			subprocess.call([opener, file])

	# def checkOutputPath(self):
	# 	if os.path.exists(self.ui.outputName):
	#

	def extractPages(self, doc):

		new_folder = ".temp"
		try:
			os.mkdir(new_folder)
		except FileExistsError:
			pass

		### ADD AN OVERWRITE FAILSAFE ###
		range_ = self.ui.rangePages.text().split("-")
		from_ = range_[0]
		to_ = range_[1] if len(range_) == 2 else (from_ + 1)
		every_ = range[2] if len(range_) == 3 else 1
		inputPdf = PdfFileReader(open(doc, "rb"))
		output = PdfFileWriter()
		for page in inputPdf.numPages[from_:to_:every_]:
			output.addPage(inputPdf.getPage(page))

		with open("test.pdf", "wb") as outputStream:
			output.write(outputStream)
		# os.remove(new_folder)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = App()
	w.show()
	sys.exit(app.exec_())
