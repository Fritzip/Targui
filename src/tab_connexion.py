# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui
import sys
try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s


class JoinTable(QtGui.QListWidget):
	def __init__(self,app,groupbox):
		QtGui.QListWidget.__init__(self,groupbox)
		self.app = app
		self.itemClicked.connect(self.item_click)
		self.itemClicked.connect(self.app.enable_button)
		self.current_item = -1
		self.setSortingEnabled(False)

	def rafraichir_tables_joindre(self,items):
		self.clear()
		for item in items:
			self.addItem(JoinTableItem(item))
			
	def item_click(self,item):
		self.current_item = item.id
		
		
class JoinTableItem(QtGui.QListWidgetItem):
    def __init__(self,item):
		self.id = item[0]
		self.pseudo = item[1]
		QtGui.QListWidgetItem.__init__(self,self.pseudo)
		

class TableEnCours(QtGui.QTreeWidget):
	def __init__(self,groupbox):
		QtGui.QTreeWidget.__init__(self,groupbox)
		self.setHeaderItem(QtGui.QTreeWidgetItem(["Joueur(s)","#","%","Temps"]))
		self.setSortingEnabled(True)
		self.setColumnWidth(0, 230)
		
		
	def rafraichir_parties_encours(self,items):
		self.clear()
		for item in items:
			i = eval(item)
			self.addTopLevelItem(TableEnCoursItem(i,self))

			
class TableEnCoursItem(QtGui.QTreeWidgetItem):
    def __init__(self,item,parent):
		self.pseudo = item[0]
		self.nb_pers = item[1]
		self.pourcentage = item[2]
		self.temps = item[3]
		QtGui.QListWidgetItem.__init__(self,parent,item)
		self.setFlags(QtCore.Qt.ItemIsEnabled)
		
class TabConnexion(QtGui.QScrollArea):
	def __init__(self,nom):
		QtGui.QScrollArea.__init__(self)
		self.nom = nom

		self.resize(600, 300)
		self.setWidgetResizable(True)
		self.setWindowTitle(u"Connexion Targui")
		self.scrollAreaWidgetContents = QtGui.QWidget()
		self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 698, 298))
		
		self.gridLayout_4 = QtGui.QGridLayout(self.scrollAreaWidgetContents)
		self.verticalLayout_2 = QtGui.QVBoxLayout()
		self.horizontalLayout = QtGui.QHBoxLayout()
		self.groupBox_2 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
		self.gridLayout_2 = QtGui.QGridLayout(self.groupBox_2)

		### Liste Tables à Joindre ###
		self.liste_joindre = JoinTable(self,self.groupBox_2)
		self.liste_joindre.setStyleSheet("outline: 0;")
		self.gridLayout_2.addWidget(self.liste_joindre, 0, 0, 1, 1)

		### Layout ###
		self.horizontalLayout.addWidget(self.groupBox_2)
		self.groupBox_3 = QtGui.QGroupBox(self.scrollAreaWidgetContents)
		self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_3)
		self.verticalLayout = QtGui.QVBoxLayout()

		### Tab de bord ###
		self.label = QtGui.QLabel(self.groupBox_3)
		self.verticalLayout.addWidget(self.label)
		spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
		self.verticalLayout.addItem(spacerItem)

		### Boutons ###
		self.but_creer = QtGui.QPushButton(self.groupBox_3)
		self.verticalLayout.addWidget(self.but_creer)
		self.but_joindre = QtGui.QPushButton(self.groupBox_3)
		self.but_joindre.setEnabled(False)
		self.verticalLayout.addWidget(self.but_joindre)
		self.but_rafraichir = QtGui.QPushButton(self.groupBox_3)
		self.verticalLayout.addWidget(self.but_rafraichir)

		### Layout ###
		self.gridLayout_3.addLayout(self.verticalLayout, 0, 0, 1, 1)
		self.horizontalLayout.addWidget(self.groupBox_3)
		self.verticalLayout_2.addLayout(self.horizontalLayout)
		self.groupBox = QtGui.QGroupBox(self.scrollAreaWidgetContents)
		self.gridLayout = QtGui.QGridLayout(self.groupBox)

		### Tree Table en Cours ###
		self.tree_encours = TableEnCours(self.groupBox)
		#self.tree_encours.resizeColumnsToContents()
		self.gridLayout.addWidget(self.tree_encours, 0, 0, 1, 1)

		### Layout ###
		self.verticalLayout_2.addWidget(self.groupBox)
		self.gridLayout_4.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
		self.setWidget(self.scrollAreaWidgetContents)
		
		self.retranslateUi()
		#QtCore.QMetaObject.connectSlotsByName(self)
		self.connect(self.liste_joindre, QtCore.SIGNAL(_fromUtf8("itemDoubleClicked(QListWidgetItem*)")), self.but_joindre.click)
		self.connect(self.liste_joindre, QtCore.SIGNAL("returnPressed()"), self.but_joindre.click)
		
	def enable_button(self):
		self.but_joindre.setEnabled(True)
		
	def retranslateUi(self):
		self.groupBox_2.setTitle(QtGui.QApplication.translate("ScrollArea", "Table(s) en attente", None, QtGui.QApplication.UnicodeUTF8))
		self.groupBox_3.setTitle(QtGui.QApplication.translate("ScrollArea", "Tableau de Bord", None, QtGui.QApplication.UnicodeUTF8))
		self.label.setText(QtGui.QApplication.translate("ScrollArea", "Hello "+self.nom, None, QtGui.QApplication.UnicodeUTF8))
		self.but_creer.setText(QtGui.QApplication.translate("ScrollArea", "Créer Table", None, QtGui.QApplication.UnicodeUTF8))
		self.but_joindre.setText(QtGui.QApplication.translate("ScrollArea", "Joindre Table", None, QtGui.QApplication.UnicodeUTF8))
		self.but_rafraichir.setText(QtGui.QApplication.translate("ScrollArea", "Rafraichir", None, QtGui.QApplication.UnicodeUTF8))
		self.groupBox.setTitle(QtGui.QApplication.translate("ScrollArea", "Partie(s) en cours", None, QtGui.QApplication.UnicodeUTF8))

		
if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	PSEUDO = sys.argv[1] if len(sys.argv)>1 else raw_input("Choisissez un pseudo : ")
	tabcon = TabConnexion(PSEUDO)
	tabcon.show()
	sys.exit(app.exec_())
	
