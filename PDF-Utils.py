#!/usr/bin/python3

import os
import subprocess
import sys
from typing import List, Union, Generator
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
		self.ui.outputName.textChanged.connect(self.enable_clear_fields)
		self.ui.readmeFile.clicked.connect(self.open_readme)
		self.pdfs: List[QtWidgets.QCheckBox] = []
		self.pdfs_text: List[str] = []
		self.show()

	def edit_selection(self) -> None:
		self.listDocs.show()

	@staticmethod
	def open_readme() -> None:
		file: str = os.path.abspath("README.md")
		if sys.platform == "win32":
			os.startfile(file)
		else:
			opener: str = "xdg-open" if sys.platform == "linux" else "open"
			subprocess.call([opener, file])

	def update_pdf_list(self) -> None:
		self.pdfs = [widget for widget in self.subwidgets(self.docsLayout) if isinstance(widget, QtWidgets.QCheckBox)]
		self.pdfs_text = [widget.text() for widget in self.pdfs]
		self.enable_clear_fields()

	def enable_clear_fields(self) -> None:
		if self.pdfs != [] or self.ui.outputName.text() != "" or self.ui.mergeDocs.isChecked() or self.ui.extractPages.isChecked():
			self.ui.clearFields.setEnabled(True)

	def enable_radios(self, pdfs: List) -> None:
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

	def add_documents(self) -> None:
		self.update_pdf_list()
		# select the first element because otherwise the filter gets added to the list, don't touch this
		additions: List[str] = QFileDialog.getOpenFileNames(self, caption="Select PDF documents", filter='PDF Files (*.pdf)')[0]
		for index, doc in enumerate(additions):
			doc: str = os.path.abspath(doc)
			if doc not in self.pdfs_text:
				checkbox = QtWidgets.QCheckBox(doc)
				checkbox.setText(doc)
				self.pdfs.append(checkbox)
				self.docsLayout.addWidget(checkbox, index)
		self.remove.setEnabled(True)
		self.enable_radios(pdfs=self.pdfs)
		self.update_pdf_list()

	@staticmethod
	def subwidgets(layout: Union[QtWidgets.QHBoxLayout, QtWidgets.QVBoxLayout, QtWidgets.QGridLayout]) -> Generator:
		widgets: Generator = (layout.itemAt(i).widget() for i in range(layout.count()))
		return widgets

	def check_remove_button(self) -> None:
		if len(self.pdfs) != 0:
			self.remove.setEnabled(True)
		else:
			self.remove.setDisabled(True)

	def remove_documents(self) -> None:
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

	def clear_fields(self) -> None:
		self.ui.openFile.setDisabled(True)
		self.ui.outputName.clear()
		for widget in self.subwidgets(self.docsLayout):
			if isinstance(widget, QtWidgets.QCheckBox):
				widget.deleteLater()
				self.pdfs.remove(widget)
		self.update_pdf_list()
		# the checkedId() method returns -1 if no radio button is checked
		if self.ui.options.checkedId() == -1:  # if no button was checked
			self.ui.mergeDocs.setDisabled(True)
			self.ui.extractPages.setDisabled(True)
		else:  # if some of the two buttons was checked
			self.ui.options.setExclusive(False)
			self.ui.options.checkedButton().setDisabled(True)
			self.ui.options.checkedButton().setChecked(False)
			self.ui.options.setExclusive(True)
		self.ui.clearFields.setDisabled(True)
		self.ui.rangePages.clear()

	def merge_docs(self, pdfs: List) -> None:
		new_file: str = self.ui.outputName.text()
		merger = PdfFileMerger(strict=False)
		if pdfs:
			for pdf in pdfs:
				with open(file=pdf, mode="rb") as file:
					file = PdfFileReader(file, strict=False)
					merger.append(file, import_bookmarks=False)
				pdfs.remove(pdf)
		merger.write(new_file)
		self.ui.openFile.setEnabled(True)

	def open_file(self) -> None:
		current_folder: str = os.getcwd()
		file: str = os.path.join(current_folder, self.ui.outputName.text())
		if sys.platform == "win32":
			os.startfile(file)
		else:
			opener: str = "xdg-open" if sys.platform == "linux" else "open"
			subprocess.call([opener, file])

	@staticmethod
	def overwrite() -> bool:
		warning = QMessageBox()
		warning.setIcon(QMessageBox.Question)
		warning.setText("The file name you have selected already exists. Do you wish to overwrite?")
		warning.setWindowTitle("Path exists.")
		warning.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
		choice = warning.exec_()
		yes, no = 16384, 65536  # the dialog emits two signals: 16384 if the users click yes, and 65536 if they click no
		choice = True if (choice == yes) else False
		return choice

	def extract_pages(self, doc: str) -> None:
		range_: List[str] = self.ui.rangePages.text().split(",")
		individual_pages: List[int] = [int(x) for x in range_ if "-" not in x]
		ranges: List[str] = [x for x in range_ if "-" in x]
		del range_
		with open(file=doc, mode="rb") as input_pdf:
			input_pdf = PdfFileReader(input_pdf)
			output_pdf = PdfFileWriter()
			page: int
			for page in individual_pages:
				output_pdf.addPage(input_pdf.getPage(page - 1))
			for range_ in ranges:
				range_: str
				range_: List[int] = [int(i) for i in range_.split("-")]
				from_: int = range_[0] - 1
				to_: int = range_[1]
				every_: int = range_[2] if len(range_) == 3 else 1
				for page in range(from_, to_, every_):
					output_pdf.addPage(input_pdf.getPage(page))
			with open(file=self.ui.outputName.text(), mode="wb") as outputStream:
				output_pdf.write(outputStream)
		self.ui.openFile.setEnabled(True)

	def execute(self) -> None:
		if os.path.exists(self.ui.outputName.text()):
			if self.overwrite():
				if self.ui.mergeDocs.isChecked():
					self.merge_docs(pdfs=self.pdfs_text)
				elif self.ui.extractPages.isChecked():
					self.extract_pages(doc=self.pdfs_text[0])
				# else:
				# SHOW WARNING
		else:
			if self.ui.mergeDocs.isChecked():
				self.merge_docs(pdfs=self.pdfs_text)
			elif self.ui.extractPages.isChecked():
				self.extract_pages(doc=self.pdfs_text[0])
			# else:
			# SHOW WARNING


if __name__ == "__main__":
	app = QApplication(sys.argv)
	w = App()
	w.show()
	sys.exit(app.exec_())
