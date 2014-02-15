# -*- coding: utf-8 -*-

import sys, random
import copy
from PyQt4 import QtGui, QtCore, Qt
# from PyQt4.QtCore import QObject, pyqtSlot

try:
	_fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
	_fromUtf8 = lambda s: s

LARG = 150
HAUT = 98

class Application(QtGui.QApplication):
	def __init__(self, argv):
		QtGui.QApplication.__init__(self, argv)
		

class MainWindowUi(QtGui.QScrollArea):
	# stopWait = QtCore.pyqtSignal()
	def __init__(self,app,pseudo_joueur, pseudo_adv):
		QtGui.QScrollArea.__init__(self)
			
		self.app = app
		self.resize(1155, 690)
		self.setWindowTitle(u"Targui "+pseudo_joueur)
		self.setWindowIcon(QtGui.QIcon('../pixmaps/icones/icone2.png')) 
		self.setWidgetResizable(True)
		
		### Grilles ###
		self.centralwidget = QtGui.QWidget()
		# self.setStyleSheet("background-image: url('../pixmaps/back/back.jpg');");
		# self.centralwidget.setBackgroundBrush(QtGui.QColor(0,255,0,125))
		self.plateau = QtGui.QGridLayout()
		self.plateau.setSpacing(0)
		self.plateau_tableaux = QtGui.QHBoxLayout()
		self.gridLayout_grand_inscroll = QtGui.QGridLayout(self.centralwidget)
		
		### Spacers ###
		spacerItem100 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		spacerItem102 = QtGui.QSpacerItem(10, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

		### Plateau ###
		self.view_plateau = {}
		self.scenes_plateau = {}
		self.cartes_plateau = {}
		
		self.listeHi = []

		self.d = {}
		
		self.hi = {}
		self.hiblanc = {}
		self.hibleu = {}
		
		self.pions = {}
		self.hipions = {}
		self.voleur = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/pions/voleur_s2.png"))
		
		# self.eventLoop = QtCore.QEventLoop()
		self.case = 0
		self.case_tab = -1
		self.option = ""
		
		for i in range(25):
			self.hi[i] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/hilight/cardHi2.png"))
			self.hibleu[i] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/hilight/cardHibleu.png"))
			self.hiblanc[i] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/hilight/cardHiblanc.png"))
			#self.pionsbleu[i] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/pions/targui_bleu_s2.png"))
			#self.pionsblanc[i] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/pions/targui_blanc_s2.png"))
		
		### Initialisation cartes Plateau ###
		liste_id = ["00","01","02","03","04","015","199","299","199","05","014","299","199","299","06","013","199","299","199","07","012","011","010","09","08"]

		### SizePolicy ###
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
		
		### Empty Scene ###
		#self.empty_scene = QtGui.QGraphicsScene(0, 0, 151, 100)
		
		
		###----------------------------Plateau--------------------------------###
		
		for i in range(25):
			chemin = self.trouveChemin(liste_id[i])
			self.cartes_plateau[i] = CartePlateau(chemin,i,liste_id[i],self.app)
			
			self.view_plateau[i] = QtGui.QGraphicsView(self.centralwidget)
			apply_conf_graph(self.view_plateau[i],sizePolicy,LARG,HAUT)
			self.view_plateau[i].setFrameShape(QtGui.QGraphicsView.NoFrame)
			self.view_plateau[i].setStyleSheet(" background-color : rgb(243,214,155);")
			
			self.scenes_plateau[i] = ScenePlateau(0, 0, LARG, HAUT,self.cartes_plateau[i],i,self.app)
			#QtGui.QGraphicsScene(0, 0, self.cartes_plateau[i].w, self.cartes_plateau[i].h)
			
			self.plateau.addWidget(self.view_plateau[i], 1+i/5, 1+i%5, 1, 1)
			
			self.view_plateau[i].setScene(self.scenes_plateau[i])
			#self.scenes_plateau[i].addItem(self.cartes_plateau[i])
		
		
		
		"""
		self.lab_visu = QtGui.QHBoxLayout()
		self.label_consigne = QtGui.QLabel() 
		self.label_consigne.setStyleSheet("border-width: 2px; border-style: solid; border-color: red;")
		self.label_consigne.setWordWrap (True)
		self.lab_visu.addWidget(self.label_consigne)
		self.lab_visu.addWidget(self.visu)
		"""
		
		### Checkboxes ###
		self.checkBoxesLayout = QtGui.QHBoxLayout()
		# self.checkBox = QtGui.QCheckBox(self)
		# self.checkBox.setChecked(True)
		# self.checkBox_2 = QtGui.QCheckBox(self)
		# self.checkBox_2.setChecked(True)
		# self.checkBox_3 = QtGui.QCheckBox(self)
		# self.checkBox_3.setChecked(True)

		spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)

		self.progressbar = QtGui.QProgressBar(self)
		self.progressbar.setValue(0)
		self.progressbar.setTextVisible(True)
		
		### Splitter Lab-But-Visu ###	
		self.splitter = QtGui.QSplitter(self)
		self.splitter.setOrientation(QtCore.Qt.Horizontal)
		self.widget1 = QtGui.QWidget(self.splitter)
		
		
		### Label Consigne ###
		self.label_consigne = QtGui.QLabel(self.widget1)
		self.label_consigne.setStyleSheet("border-width: 2px; border-style: solid; border-color: red;")
		self.label_consigne.setWordWrap (True)
		self.connect(self.label_consigne, QtCore.SIGNAL("linkActivated(QString)"), self.getLinkId) 
		
		
        ### Visualisation instantanee ###
		self.scene_visu = QtGui.QGraphicsScene(0, 0, 1.5*LARG, 1.5*HAUT)
		self.visu = QtGui.QGraphicsView(self.splitter)
		sizePolicy.setHeightForWidth(self.visu.sizePolicy().hasHeightForWidth())
		self.visu.setSizePolicy(sizePolicy)
		self.visu.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.visu.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.visu.setMaximumSize(QtCore.QSize(LARG*1.5, 1.5*HAUT))
		self.visu.setMinimumSize(QtCore.QSize(0, 1.5*HAUT))
		self.visu.setScene(self.scene_visu)
		

		### Splitter Colonne Droite ###
		self.colonne_droite = QtGui.QSplitter()
		self.colonne_droite.setOrientation(QtCore.Qt.Vertical)
		
		
		### Tableaux de bord ### 
		self.joueur = Joueur(self.colonne_droite,sizePolicy,pseudo_joueur, self.app)
		self.adversaire = Adversaire(self.colonne_droite,sizePolicy,pseudo_adv, self.app)
		
		
		### Tchat ###
		self.browser = QtGui.QTextBrowser(self.colonne_droite)
		self.lineedit = QtGui.QLineEdit(self.colonne_droite)
		self.lineedit.setPlaceholderText("Tchat")
		self.lineedit.setMaximumSize(365,25)
		
		self.connect(self.lineedit, QtCore.SIGNAL("returnPressed()"), self.update_chat)
		
		
		### Affichage Checkboxes ###
		# self.checkBoxesLayout.addWidget(self.checkBox)		
		# self.checkBoxesLayout.addWidget(self.checkBox_2)		
		# self.checkBoxesLayout.addWidget(self.checkBox_3)
		self.checkBoxesLayout.addWidget(self.progressbar)
		self.checkBoxesLayout.addItem(spacerItem)

		
		### Affichage Lab-But ###
		self.labButVisuLayout = QtGui.QHBoxLayout(self.widget1)
		self.labButVisuLayout.setMargin(0)
		self.labButVisuLayout.addWidget(self.label_consigne)
		
    ### Affichage Colonne Gauche ###
		self.colonne_gauche = QtGui.QVBoxLayout()
		self.colonne_gauche.addItem(spacerItem102)
		self.colonne_gauche.addLayout(self.checkBoxesLayout)
		self.colonne_gauche.addWidget(self.splitter)
		self.colonne_gauche.addLayout(self.plateau)
		self.colonne_gauche.addItem(spacerItem102)
		
		### Affichage Général ###
		self.plateau_tableaux.addItem(spacerItem100)
		self.plateau_tableaux.addLayout(self.colonne_gauche)
		self.plateau_tableaux.addItem(spacerItem100)
		self.plateau_tableaux.addWidget(self.colonne_droite)
		
		self.colonne_droite.setSizes([255,255,30,25])
		
		### Affichage Final ###
		self.gridLayout_grand_inscroll.addLayout(self.plateau_tableaux, 0, 0, 1, 1)
		self.setWidget(self.centralwidget)
		
		# self.show()

		
		###########################################################################
		###								Fonctions								###
		###########################################################################

	def setConsignes(self,lab):
		#cur_lab = self.label_consigne.text()
		#print cur_lab,[cur_lab],type(cur_lab)
		#if cur_lab[0:4] =="<qt>":
		#	cur_lab = ""
		#lab_hist = cur_lab.split('\n')
		#print lab_hist,[lab_hist],type(lab_hist)
		# "".join(lab_hist[-5:])+'\n'+
		setText(self.label_consigne,self.formateMessage(lab))

	def wait(self): 
		self.stopWait.connect(self.eventLoop.quit)   
		self.eventLoop.exec_()
	
	def formateMessage(self,message_formate):
		liste = message_formate.split('*')
		final = ""
		for i in range(len(liste)):
			if i%2==0:
				final+=liste[i]
			elif i%2==1:
				final+= "<a href="+str(liste[i]).replace(" ","")+">"+liste[i]+"</a>"
		final = "<qt>"+final+"</qt>"	
		return final
		
	def getLinkId(self,id): 
		self.option = id
		
	def quitter(self): 
		self.app.exit(0)
		
	def update_chat(self):
		message = self.lineedit.text()
		self.emit(QtCore.SIGNAL("envoyer_message"),message)
		self.lineedit.clear()

	def chat_reception(self,message):
		message = "".join(message.split("\x00\x00\x00"))
		self.browser.append(message)
				
	def trouveChemin(self, id_card):
		if id_card[0]=='0':
			return "../pixmaps/cartes_contour/"+id_card+".png"
		elif id_card[0]=='1':
			return "../pixmaps/cartes_marchandises/"+id_card+".png"
		elif id_card[0]=='2':
			return "../pixmaps/cartes_tribus/"+id_card+".png"
		else:
			return "../pixmaps/cartes_ex/2.png"
	
	def supprimer_pion(self,emplacement):
		self.scenes_plateau[emplacement].removeItem(self.pions[emplacement])
		#self.scenes_plateau[emplacement].removeItem(self.hipions[emplacement])
		self.pions.__delitem__(emplacement)
		#self.hipions.__delitem__(emplacement)
		
	def supprimer_tout_pions(self):
		for i in self.pions.keys():
			self.scenes_plateau[i].removeItem(self.pions[i])
			#self.scenes_plateau[i].removeItem(self.hipions[i])
		self.pions.clear()		
		#self.hipions.clear()
	
	def supprimer_tout_hilight(self):
		for i in self.hipions.keys():
			#self.scenes_plateau[i].removeItem(self.pions[i])
			self.scenes_plateau[i].removeItem(self.hipions[i])
		#self.pions.clear()		
		self.hipions.clear()
			
	def suppr_carte(self, emplacement):
		self.scenes_plateau[emplacement].removeItem(self.cartes_plateau[emplacement])
		# if self.case == emplacement :
			# try : self.scene_visu.removeItem(self.scene_visu.items()[0])
			# except : pass

	def nettoyer_cache(self):
		for i in self.scene_visu.items():
			self.scene_visu.removeItem(i)
		
	def nouvelle_carte(self,id_card, emplacement,categorie):
		self.cartes_plateau[emplacement] = CartePlateau(self.trouveChemin(id_card),emplacement,id_card,self.app,categorie)
		self.scenes_plateau[emplacement].addItem(self.cartes_plateau[emplacement])
	
	def modifier_carte(self,(emplacement,id_card,categorie)):
		self.suppr_carte(emplacement)
		self.nouvelle_carte(str(id_card),emplacement, categorie)

	def change_carte_to_marchandise(self,emplacement):
		self.modifier_carte((emplacement,199,"marchandise"))

	def change_carte_to_tribu(self,emplacement):
		self.modifier_carte((emplacement,299,"tribu"))
		
	def affichage_targui(self,param):
		couleur, emplacement = param
		self.pions[emplacement] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/pions/targui_"+couleur+"_s2.png"))
		self.hipions[emplacement] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/hilight/cardHi"+couleur+".png"))
		self.pions[emplacement].setPos(0,20)
		self.scenes_plateau[emplacement].addItem(self.pions[emplacement])
		self.scenes_plateau[emplacement].addItem(self.hipions[emplacement])
	
	def affichage_voleur(self, emplacement) :
		self.scenes_plateau[emplacement].addItem(self.voleur)
		
	def affichage_marqueur(self, param):
		couleur = param[0]
		emplacement = param[1]
		self.pions[emplacement] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/pions/marqueur_"+couleur+"_s.png"))
		#self.hipions[emplacement] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/hilight/cardHi"+couleur+".png"))
		self.pions[emplacement].setPos(0,35)
		self.scenes_plateau[emplacement].addItem(self.pions[emplacement])
		#self.scenes_plateau[emplacement].addItem(self.hipions[emplacement])

	def deplacer_marqueur(self,param):
		emplacement = int(param[0])
		destination = int(param[1])
		pion = self.pions[emplacement]
		self.supprimer_pion(emplacement)
		self.pions[destination] = pion
		self.pions[destination].setPos(0,35)
		self.scenes_plateau[destination].addItem(self.pions[destination])

	def hi_consignes(self):
		self.label_consigne.setStyleSheet("border-width: 2px; border-style: solid; border-color: red;")

	def deshi_consignes(self):
		self.label_consigne.setStyleSheet("")

	def corresp_hi(self,i,couleur):
		return eval("self.hi"+couleur+"[i]")
		
	def plateau_hi(self, param):
		liste = param[0]
		couleur = param[1] if len(param)>1 else "" 
		self.plateau_decliquable()
		self.listeHi = copy.deepcopy(liste)
		for i in liste:
			self.d[i] = self.corresp_hi(i,couleur)
			self.scenes_plateau[i].addItem(self.d[i])
		
	def allow_clic(self):
		for i in self.listeHi:
			self.scenes_plateau[i].setClicable(True)
			self.view_plateau[i].viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor))
		
	def plateau_decliquable(self):
		for i in self.listeHi:
			self.scenes_plateau[i].setClicable(False)
			self.scenes_plateau[i].removeItem(self.d[i])
			self.view_plateau[i].viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))	
		self.listeHi = []

			#-----------#
			
	def plateau_hi_tab(self, liste):
		self.joueur.plateau_hi(liste)

	def allow_clic_tab(self):
		self.joueur.allow_clic()

	def plateau_decliquable_tab(self):
		self.joueur.plateau_decliquable()

		    #-----------#
		
		
	def update_ressources_perso(self,dico):
		for i in dico.keys():
			self.joueur.label_ressources[i].setText(str(dico[i]))
			
	def update_ressources_adv(self,dico):
		for i in dico.keys():
			self.adversaire.label_ressources[i].setText(str(dico[i]))
	
	def update_ressources(self,param):
		perso = param[0]
		adv = param[1]
		self.update_ressources_perso(perso)
		self.update_ressources_adv(adv)
		
	def transferer_carte_achat(self,param):
		emplacement_s = param[0] # Emplacement sur le plateau
		emplacement_d = param[1] # Emplacement tableau
		joueur = eval("self."+param[2])
		joueur.cartes_tableau[emplacement_d] = CarteTableau("../pixmaps/symboles/"+self.cartes_plateau[emplacement_s].categorie+".jpg",emplacement_d,self.cartes_plateau[emplacement_s], self.app)
		joueur.scenes_tableau[emplacement_d].addItem(joueur.cartes_tableau[emplacement_d])
	
	def update_pseudo_adv(self,pseudo_adv):
		self.adversaire.label.setText(pseudo_adv)

	def update_couleur(self,couleur):
		Bleu = QtGui.QColor(49,64,206)
		Blanc = QtGui.QColor(156,157,165)
		qcolor = eval(couleur)
		if couleur == "Blanc":
			qcolor_adv = Bleu
		elif couleur == "Bleu":
			qcolor_adv = Blanc
		self.joueur.codid.couleur = qcolor
		self.adversaire.codid.couleur = qcolor_adv
			
	def update_pourcentage(self,pourcentage):
		self.progressbar.setValue(pourcentage)

	def closeEvent(self, event):
		quit_msg = "Êtes-vous sûr de vouloir quitter le jeu ?\n Ceci arrêtera définitivement la partie en cours."
		quit_msg = QtGui.QApplication.translate("MainWindow", quit_msg, None, QtGui.QApplication.UnicodeUTF8)
		reply = QtGui.QMessageBox.question(self, 'Message', 
										   quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
		
		if reply == QtGui.QMessageBox.Yes:
			self.emit(QtCore.SIGNAL("fin_jeu"))
			event.accept()		 
		else:					 
			event.ignore()

		
###########################################################################
###						Fonctions Globales								###
###########################################################################
def setText(label,text):
	label.setText(QtGui.QApplication.translate("MainWindow", text, None, QtGui.QApplication.UnicodeUTF8))
	label.repaint()
	
def get_emplacement(emplacement, event):
	return (emplacement, event)
	
def apply_conf_graph(graph,sizePol,w,h):
	apply_conf_sizePolicy(graph,sizePol)
	graph.setMinimumSize(QtCore.QSize(w, h))
	graph.setMaximumSize(QtCore.QSize(w, h))
	graph.setAutoFillBackground(False)
	graph.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
	graph.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
	
def apply_conf_grid(grid,vs,hs):	
	grid.setVerticalSpacing(vs)
	grid.setHorizontalSpacing(hs)
	
def apply_conf_label(lab):	
	lab.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
	
def apply_conf_sizePolicy(QWi,sizePol):	
	sizePol.setHorizontalStretch(0)
	sizePol.setVerticalStretch(0)
	#sizePol.setHeightForWidth(QWi.sizePolicy().hasHeightForWidth())
	QWi.setSizePolicy(sizePol)


###########################################################################
###						   	Identifiant Couleur							###
###########################################################################

class Point(QtGui.QWidget):
	def __init__(self, couleur):
		super(Point, self).__init__()
		self.couleur = couleur
		
	def paintEvent(self,event):
		self.qp=QtGui.QPainter()
		self.qp.begin(self)
		self.qp.setPen(self.couleur)
		self.qp.setBrush(self.couleur)
		self.qp.drawEllipse(3,3,9,9)
		self.qp.end()

		
###########################################################################
###								Cartes Plateau							###
###########################################################################
    
class CartePlateau(QtGui.QGraphicsPixmapItem):
	def __init__(self, nom_carte,i,id_card ,app, categ=""):
		self.categorie = categ 
		self.app = app
		self.id_card = id_card
		self.nom = nom_carte
		self.image = QtGui.QPixmap(nom_carte)
		self.image_scaled = QtGui.QGraphicsPixmapItem(self.image.scaled(LARG*1.5,HAUT*1.5, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation))
		self.emplacement = i
		QtGui.QGraphicsPixmapItem.__init__(self, self.image)
		self.pix = QtGui.QGraphicsPixmapItem(self.image)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)
		self.setAcceptHoverEvents(True)
		
	def hoverEnterEvent(self, e):
		self.app.MainWindow.scene_visu.addItem(self.image_scaled)
		
	def hoverLeaveEvent(self, e):
		self.app.MainWindow.scene_visu.removeItem(self.image_scaled)


###########################################################################
###							Cartes Tableau								###
###########################################################################
		
class CarteTableau(QtGui.QGraphicsPixmapItem):
	def __init__(self, chemin,i,carte, app):
		self.image = QtGui.QPixmap(chemin)
		QtGui.QGraphicsPixmapItem.__init__(self, self.image)
		self.pix = QtGui.QGraphicsPixmapItem(self.image)
		self.carte_visu = carte.image_scaled
		self.emplacement = i
		self.setAcceptHoverEvents(True)
		self.app = app
		
	def hoverEnterEvent(self, e):
		self.app.MainWindow.scene_visu.addItem(self.carte_visu)
		
	def hoverLeaveEvent(self, e):
		self.app.MainWindow.scene_visu.removeItem(self.carte_visu)

		
###########################################################################
###							Ressources									###
###########################################################################
		
class Ressource(QtGui.QGraphicsPixmapItem):
	def __init__(self, ressource):
		self.image = QtGui.QPixmap("../pixmaps/ressources/"+str(ressource))
		self.w = self.image.width()
		self.h = self.image.height()
		self.emplacement = ressource
		QtGui.QGraphicsPixmapItem.__init__(self, self.image)
		self.pix = QtGui.QGraphicsPixmapItem(self.image)
		self.setFlag(QtGui.QGraphicsItem.ItemIsSelectable, False)

		
###########################################################################
###							Scene Tableau								###
###########################################################################
		
class SceneTableau(QtGui.QGraphicsScene):
	def __init__(self,i,a,b,w,h,app):
		QtGui.QGraphicsScene.__init__(self,a,b,w,h)
		self.emplacement = i
		self.clicable = False
		self.app = app

	def isClicable(self):
			return self.clicable
			
	def setClicable(self, bool):
			self.clicable = bool
	 
	def mouseReleaseEvent(self, event):
		if self.isClicable():
			super(SceneTableau, self).mouseReleaseEvent(event)
			self.app.MainWindow.case_tab = self.emplacement
			# self.app.MainWindow.stopWait.emit()
    

###########################################################################
###							Scene Plateau								###
###########################################################################
			
class ScenePlateau(QtGui.QGraphicsScene):
	def __init__(self,a,b,w,h,carte,i,app):
		QtGui.QGraphicsScene.__init__(self,a,b,w,h)
		self.addItem(carte)
		self.emplacement = i
		self.clicable = False
		self.app = app
		
	def isClicable(self):
			return self.clicable
			
	def setClicable(self, bool):
			self.clicable = bool
		
	def mouseReleaseEvent(self, event):
		if self.isClicable():
			super(ScenePlateau, self).mouseReleaseEvent(event)
			self.app.MainWindow.case = self.emplacement
			# self.app.MainWindow.stopWait.emit()

			
###########################################################################
###							TabDeBord									###
###########################################################################
class TabDeBord(QtGui.QScrollArea):
	def __init__(self,centralwidget,sizePol, nom, couleur, app):
		QtGui.QScrollArea.__init__(self,centralwidget)
		self.setWidgetResizable(True)
		
		self.setFrameShape(QtGui.QFrame.NoFrame)
		self.setFrameShadow(QtGui.QFrame.Raised)
		self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

		self.app = app
		
		### Joueur ###
		self.nom = nom
		self.couleur = couleur
		
		### Tableau ###
		self.view_tableau = {}
		self.scenes_tableau = {}
		self.cartes_tableau = {}
		
		### Ressources ###
		self.view_ressources = {}
		self.scenes_ressources = {}
		self.cartes_ressources = {}
		self.label_ressources = {}
		self.corresp = {0:"dattes",1:"poivre",2:"sel",3:"or",4:"pv"}
		
		self.frame = QtGui.QFrame()
		self.frame.setFrameShape(QtGui.QFrame.NoFrame)
		self.frame.setFrameShadow(QtGui.QFrame.Raised)
		self.frame.setMaximumSize(QtCore.QSize(360, 255))
		self.frame.setMinimumSize(QtCore.QSize(360, 255))
		self.sizePolicy = sizePol
		apply_conf_sizePolicy(self.frame,self.sizePolicy)
		
		self.gridLayout_5 = QtGui.QGridLayout(self.frame)
		self.gridLayout_5.setMargin(0)
		self.gridLayout_5.setSpacing(0)
		self.verticalLayout_3 = QtGui.QVBoxLayout()
		self.verticalLayout_3.setSpacing(0)
		self.horizontalLayout_2 = QtGui.QHBoxLayout()

		self.codid = Point(self.couleur)
		self.codid.setMaximumSize(QtCore.QSize(20,15))
		self.codid.setMinimumSize(QtCore.QSize(20,15))
		
		self.label = QtGui.QLabel(self)
		# self.label.setStyleSheet("border-width: 2px; border-style: solid; border-color: red;")
		self.label.setText(QtGui.QApplication.translate("MainWindow", self.nom, None, QtGui.QApplication.UnicodeUTF8))

		self.horizontalLayout_2.addWidget(self.codid)
		self.horizontalLayout_2.addWidget(self.label)
		spacerItem4 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.horizontalLayout_2.addItem(spacerItem4)
		self.verticalLayout_3.addLayout(self.horizontalLayout_2)
		self.horizontalLayout = QtGui.QHBoxLayout()
		self.gridLayout_2 = QtGui.QGridLayout()
		self.gridLayout_2.setSpacing(1)
		
		
		###--------------------------Tableau de bord------------------------------###
		
		for i in range(12):
			self.view_tableau[i] = QtGui.QGraphicsView()
			apply_conf_graph(self.view_tableau[i],self.sizePolicy,50,76)
			self.scenes_tableau[i] = SceneTableau(i,0, 0, 50, 76, self.app)
			self.view_tableau[i].setScene(self.scenes_tableau[i])
			# self.view_tableau[i].setBackgroundBrush(QtGui.QColor(0,255,0,125))
			self.gridLayout_2.addWidget(self.view_tableau[i], i/4,i%4 , 1, 1)
			
		self.horizontalLayout.addLayout(self.gridLayout_2)
		spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.horizontalLayout.addItem(spacerItem5)
		self.verticalLayout_2 = QtGui.QVBoxLayout()
		self.verticalLayout = QtGui.QVBoxLayout()
		self.verticalLayout.setSpacing(0)
		
		###---------------------------Ressources------------------------------###
		self.gridRessources_1 = QtGui.QGridLayout()
		apply_conf_grid(self.gridRessources_1,0,10)
		
		self.gridRessources_2 = QtGui.QGridLayout()
		apply_conf_grid(self.gridRessources_2,0,10)
		
		for j,i in enumerate(["dattes","poivre","sel"]):
			self.view_ressources[i] = QtGui.QGraphicsView()
			apply_conf_graph(self.view_ressources[i],self.sizePolicy,35,35)
			self.label_ressources[i] = QtGui.QLabel()
			apply_conf_label(self.label_ressources[i])
			self.scenes_ressources[i] = QtGui.QGraphicsScene(0, 0, 35, 35)
			self.view_ressources[i].setScene(self.scenes_ressources[i])
			self.gridRessources_1.addWidget(self.view_ressources[i], 0, j, 1, 1)
			self.gridRessources_1.addWidget(self.label_ressources[i], 1, j, 1, 1)
			self.cartes_ressources[i] = Ressource(i)
			self.scenes_ressources[i].addItem(self.cartes_ressources[i])
			
		for j,i in enumerate(["or","pv"]):
			self.view_ressources[i] = QtGui.QGraphicsView()
			
			if j==0:
				apply_conf_graph(self.view_ressources[i],self.sizePolicy,34,35)
				self.scenes_ressources[i] = QtGui.QGraphicsScene(0, 0, 34, 35)
			elif j==1:
				apply_conf_graph(self.view_ressources[i],self.sizePolicy,47,35)
				self.scenes_ressources[i] = QtGui.QGraphicsScene(0, 0, 47, 35)
			
			self.view_ressources[i].setScene(self.scenes_ressources[i])
			self.label_ressources[i] = QtGui.QLabel()
			apply_conf_label(self.label_ressources[i])
			self.gridRessources_2.addWidget(self.view_ressources[i], 0, j, 1, 1)
			self.gridRessources_2.addWidget(self.label_ressources[i], 1, j, 1, 1)
			self.cartes_ressources[i] = Ressource(i)
			self.scenes_ressources[i].addItem(self.cartes_ressources[i])
			
		spacerItemRessources = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
		self.gridRessources_1.addItem(spacerItemRessources, 0, 3, 1, 1)
		self.gridRessources_2.addItem(spacerItemRessources, 0, 2, 1, 1)
		
		self.verticalLayout.addLayout(self.gridRessources_1)
		self.verticalLayout.addLayout(self.gridRessources_2)
		self.verticalLayout_2.addLayout(self.verticalLayout)
		
		###--------------------------Carte en main------------------------------###
		self.carte_main_vide = QtGui.QPixmap("../pixmaps/cartes_tribus/299.png")
		self.carte_main_vide = self.carte_main_vide.scaled(LARG,HAUT, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.FastTransformation)
		self.carte_main_vide = QtGui.QGraphicsPixmapItem(self.carte_main_vide)
		self.view_main = QtGui.QGraphicsView()
		apply_conf_graph(self.view_main,self.sizePolicy,LARG,HAUT)
		self.view_main.setAlignment(QtCore.Qt.AlignCenter)
		
		self.verticalLayout_2.addWidget(self.view_main)
		
		self.scenes_main = QtGui.QGraphicsScene(0, 0, LARG, HAUT)
		
		self.view_main.setScene(self.scenes_main)
		self.scenes_main.addItem(self.carte_main_vide)
		
		### Affichage ###
		self.horizontalLayout.addLayout(self.verticalLayout_2)
		self.verticalLayout_3.addLayout(self.horizontalLayout)
		self.gridLayout_5.addLayout(self.verticalLayout_3, 0, 0, 1, 1)
		self.setWidget(self.frame)


###########################################################################
###		       Joueur & Adversaire (hérite de TabDeBord)  	    		###
###########################################################################
		
class Joueur(TabDeBord):
	def __init__(self, centralwidget, sizePol, nom, app):
		self.couleur = QtGui.QColor(0,250,0)
		TabDeBord.__init__(self,centralwidget,sizePol,nom, self.couleur, app)	
		
		sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
		self.setMinimumSize(QtCore.QSize(365, 255))
		self.setMaximumSize(QtCore.QSize(365, 255))
		self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)	
		
		self.listeHi = []
		
		self.hi = {}
				
		for i in range(12):
			self.hi[i] = QtGui.QGraphicsPixmapItem(QtGui.QPixmap("../pixmaps/hilight/symbHi.png"))
		
	def plateau_hi(self, liste):
		# self.plateau_decliquable()
		self.listeHi = copy.deepcopy(liste)
		for i in liste:
			self.scenes_tableau[i].addItem(self.hi[i])
		
	def allow_clic(self):
		for i in self.listeHi:
			self.scenes_tableau[i].setClicable(True)
			self.view_tableau[i].viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.PointingHandCursor))

	def plateau_decliquable(self):
		for i in self.listeHi:
			self.scenes_tableau[i].setClicable(False)
			self.scenes_tableau[i].removeItem(self.hi[i])
			self.view_tableau[i].viewport().setProperty("cursor", QtGui.QCursor(QtCore.Qt.ArrowCursor))	

##-------------------------------------------------------------------------##
			
class Adversaire(TabDeBord):
	def __init__(self, centralwidget, sizePol, nom, app):
		self.couleur = QtGui.QColor(250,0,0)
		TabDeBord.__init__(self,centralwidget,sizePol,nom, self.couleur, app)

		
		self.setMinimumSize(QtCore.QSize(365, 0))
		self.setMaximumSize(QtCore.QSize(365, 255))

		
###########################################################################
###								Main()									###
###########################################################################
		
if __name__ == '__main__':
	fen = Application(sys.argv)
	PSEUDO = sys.argv[1] if len(sys.argv)>1 else raw_input("Choisissez un pseudo : ")
	fen.MainWindow = MainWindowUi(fen, PSEUDO, "Attente d'un second joueur")
	ui = fen.MainWindow
	ui.joueur.label.update()
	sys.exit(fen.exec_())

