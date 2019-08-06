import os
import sys
import subprocess
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from PyQt5.QtWidgets import QApplication, QFileDialog, QDialog, QMessageBox, QMainWindow
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
		self.ui.extractPages.toggled.connect(self.ui.rangePages.setEnabled)
		self.ui.openFile.setDisabled(True)
		self.ui.clearFields.clicked.connect(self.clearFields)
		self.ui.selectDocs.clicked.connect(self.selectDocuments)
		self.listDocs = QDialog(self)
		self.docsLayout = QtWidgets.QVBoxLayout(self.listDocs)
		self.ui.editListOfDocs.clicked.connect(self.listDocs.show)
		self.show()

	# def createListDocs(self):

	def selectDocuments(self):
		pdfs = QFileDialog.getOpenFileNames(self, caption="Select PDF documents", filter='PDF Files (*.pdf)')
		pdfs = [pdf for pdf in pdfs][0]
		for index, doc in enumerate(pdfs):
			checkbox = QtWidgets.QCheckBox(doc)
			checkbox.setText(doc)
			checkbox.setChecked(True)
			self.docsLayout.addWidget(checkbox)
			self.docsLayout.setAlignment(Qt.AlignLeft)

	def clearFields(self):
		self.ui.openFile.setDisabled(True)
		self.ui.outputName.clear()

	def mergeDocs(self):
		new_file = self.ui.outputName.text()
		# pdfs = [pdf for pdf in sorted(os.listdir(os.getcwd()), key=os.path.getmtime) if pdf.endswith(".pdf")]
		pdfs = [pdf for pdf in sorted(os.listdir(os.getcwd()), key=os.path.getmtime) if pdf.endswith(".pdf")]
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

	def extractPages(self, doc):

		new_folder = ".temp"
		try:
			os.mkdir(new_folder)
		except FileExistsError:
			pass

		### ADD AN OVERWRITE FAILSAFE ###

		range_ = self.ui.rangePages.text()
		range_ = range_.split("-")
		from_ = range_[0]
		to_ = range_[1]
		every_ = range[2] if len(range_) == 3 else 1
		inputPdf = PdfFileReader(open(doc, "rb"))
		output = PdfFileWriter()
		for page in inputPdf.numPages[from_:to_:every_]:
			output.addPage(inputPdf.getPage(page))

		with open("test.pdf", "wb") as outputStream:
			output.write(outputStream)


if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = App()
	w.show()
	sys.exit(app.exec_())
