#! /usr/bin/python
# -*- coding: utf-8 -*-

####-------CLIENT du jeu TARGUI-------####

#----RESUME
#																							
# - ThreadJeu(soket_client,ui) -> Gestion des parties																									
# - ThreadTchatRec(socket_tchat) -> Reçoit les messages 
#									instantanés des clients
# - ThreadTchatEm(socket_tchat) -> Transmet les messages des clients	
#
#--------------------

# Librairies :
import socket, sys, threading, time, select

# Autres fichiers :
from targui_gui import *
from targui_jeu_gui import *
from tab_connexion import *

## Variables globales ##
HOST= "127.0.0.1" 
PORT_J = 8012 # Pour le jeu
PORT_T = 8021  # Pour le tchat
PSEUDO = ""

# Usage python client_targui.py -n nom [-ip ip] [-pj port_jeu] [-pt port_tchat]
if len(sys.argv) > 1:
	for i in range(len(sys.argv)):
		if sys.argv[i]=='-ip':
			HOST = str(sys.argv[i+1])
		elif sys.argv[i]=='-pj':
			PORT_J = int(sys.argv[i+1])
		elif sys.argv[i]=='-pt':
			PORT_T = int(sys.argv[i+1])
		elif sys.argv[i]=='-n':
			PSEUDO = sys.argv[i+1]

if PSEUDO == "": PSEUDO = raw_input("Usage : python client_targui.py -n nom \nChoisissez un pseudo : ")
#################################################
class ThreadJeu(QtCore.QThread):  

	""" Thread associée au déroulement du jeu côté client """

	#----------------------------------------------------------	
	def __init__(self, conn, ui):
		QtCore.QThread.__init__(self)
		self.connexion = conn  # réf. du socket de connexion
		self.ui = ui
		self.choix = ''

	#----------------------------------------------------------		
	def run(self):
		global PSEUDO
		self.send(PSEUDO)
		
		try:
			jeu = True
			while True : # Attente d'un message démarrant le jeu
			
				message_recu = self.rec()
			
				# Choix d'une table de jeu :
				if message_recu == "choix_table":
					self.rafraichir()
					self.choix_table()
				
				# Lancement d'une partie
				elif  message_recu == "start" : break
				
				# Arrêt de la connexion :
				elif not message_recu or message_recu.upper() == "STOP" : 
					jeu = False
					break
				
				# Attente d'un autre joueur pour lancer la partie
				elif message_recu == "attente":
					self.emit(QtCore.SIGNAL("show_game"))
					self.emit(QtCore.SIGNAL("close_tabcon"))
				time.sleep(0.1)
				
			if jeu :
			
				#----------------#
				# Début partie   #
				#----------------#
		
				# Attribution d'une couleur
				couleur = self.rec()
				self.emit(QtCore.SIGNAL("update_couleur"),couleur)
		
				# Initialisation du pseudo adverse :
				pseudo_adv = self.rec()
				self.emit(QtCore.SIGNAL("update_pseudo_adv"),pseudo_adv)
		
				# On démarre la partie :
				self.partie()
		
				# Fin de partie :
				self.connexion.close()
		
		except:
			self.emit(QtCore.SIGNAL("fermeture"))
			self.connexion.close()

	#----------------------------------------------------------
	def partie(self) :
					
		while True:
			info = self.rec()
			if info == "break": break # Fin de partie
			elif info == "go" : # On fait une manche					
				self.update_plateau()
				self.phase1()
				self.phase2()
				self.phase3()
				self.fin_manche()
			else : # Action du voleur
				self.voleur(info)
			time.sleep(0.1)
		res = self.rec() # Résultat du jeu
		self.emit(QtCore.SIGNAL("setC"),res)



####-----------------FONCTIONS DU JEU-----------------####

	#----------------------------------------------------------
	def rafraichir(self):
	
		""" Met à jour l'affichage graphique de la fenêtre de connexion"""
		
		tables = eval(self.rec())
		self.emit(QtCore.SIGNAL("rafraichir_tables_joindre"),tables)

		parties_en_cours  = eval(self.rec())
		self.emit(QtCore.SIGNAL("rafraichir_parties_encours"),parties_en_cours)

	#----------------------------------------------------------	
	def choix_table(self) :
	
		""" Fonction associée au choix de la table de jeu """
		
		while self.choix == '' : time.sleep(0.01)
		self.send(self.choix)
		self.choix = ''

	#----------------------------------------------------------
	def joindre_table(self):
	
		""" Lorsque le choix est de joindre une table existante"""
		
		id_table = tabcon.liste_joindre.current_item 
		self.choix = id_table

	#----------------------------------------------------------		
	def creer_table(self): self.choix = 'n'
	
	#----------------------------------------------------------	
	def rafraichir_tables(self): self.choix = 'r'
	
	#----------------------------------------------------------	
	def update_plateau(self) :
		
		"""Mise à jour du plateau : cartes, position voleur, 
		ressources, emplacement cliquable..."""
		
		#-----------------#
		# Update Plateau  #
		#-----------------#
				
		# Réception des paramètres nécessaires :
		cartes = eval(self.rec())
		plateau_hi = self.rec()
		voleur = eval(self.rec())
		
		## Signaux pour l'interface graphique :
		self.emit(QtCore.SIGNAL("voleur"),voleur)
		self.emit(QtCore.SIGNAL("plateau_hi"),[eval(plateau_hi)])
		
		for carte in cartes :
			self.emit(QtCore.SIGNAL("cartes"),carte)
		
		# Miste à jour des ressources par joueur et de la 
		# progression du jeu :	
		self.update_ressources()
		self.update_pourcentage()	

	#----------------------------------------------------------	
	def phase1(self):
	
		"""Phase I : Placement des targuis"""
		
		for j in range(6) : 
			lab = self.rec()
			consigne = self.rec()
		
			# Joueur en cours
			if consigne == "go" :
				self.emit(QtCore.SIGNAL("allow_clic"))
				self.emit(QtCore.SIGNAL("setC"),lab)
				
				# Boucle jusqu'à ce que le joueur clic
				self.choix_case()
			
			# Joueur en attente	
			elif consigne == "wait" : 
				self.emit(QtCore.SIGNAL("setC"),lab)
			
			# On met à jour le plateau et les targuis
			plateau_hi = eval(self.rec())
			self.emit(QtCore.SIGNAL("plateau_hi"),[plateau_hi])
			case = self.rec()
			targui = self.rec()
			self.emit(QtCore.SIGNAL("targui"),(targui,int(case)))
			
		self.update_pourcentage()
			
	#------------------------------------------------------
	def phase2(self):
	
		""" Phase II : Placement des marqueurs """
		
		marqueurs = eval(self.rec())
		for marqueur in marqueurs :
			self.emit(QtCore.SIGNAL("affichage_marqueur"),marqueur)
		
	#------------------------------------------------------
	def phase3(self):
		
		""" Phase III : Récupération des pions """
		
		self.update_pourcentage()	
		self.emit(QtCore.SIGNAL("supprimer_tout_hilight"))

		for i in range(2):
			lab = self.rec()
			self.emit(QtCore.SIGNAL("setC"),ui.formateMessage(lab))
			
			# Joueur ou non joueur
			consigne = self.rec()
			
			while True:
				info = self.rec()
				if info == "break": break
				
				# Le joueur récupère une couleur et les cases cliquables
				couleur = self.rec()
				cliquable = eval(self.rec())
				
				# Si le client est le joueur en cours :
				if consigne == "joueur" :
					self.emit(QtCore.SIGNAL("plateau_hi"),[cliquable])
					self.emit(QtCore.SIGNAL("allow_clic"))
					
					# Boucle en attente d'un clic client 
					ack = self.choix_case()
					
				# Sinon le client attent
				elif consigne == "adversaire" : 
					self.emit(QtCore.SIGNAL("plateau_hi"),\
					[cliquable,couleur])

				case = int(self.rec())					
				action = self.rec() 
				
				# Fonctions différentes en fonction de l'action 
				# choisit :
				
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				if action == "marchandise_targui":
					lab = self.rec()
					self.emit(QtCore.SIGNAL("setC"),lab)

				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~					
				elif action == "marchandise_marqueur":
					lab = self.rec()
					self.emit(QtCore.SIGNAL("setC"),lab)
					self.emit(QtCore.SIGNAL("nettoyer_cache"))
					self.emit(QtCore.SIGNAL("change_carte_to_tribu"),case)

				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~				
				elif action == "tribus_marqueur":
					self.gestion_tribus(case, consigne)
					
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
				elif action == "caravane" :
				
					# Résultat de l'action : 
					res = self.rec()
					self.emit(QtCore.SIGNAL("plateau_decliquable"))
					self.emit(QtCore.SIGNAL("setC"),res)
				
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~	
				elif action == "expansion_tribale" :
				
					# Mise à jour de la consigne de l'action :
					lab = self.rec()
					self.emit(QtCore.SIGNAL("plateau_decliquable"))
					self.emit(QtCore.SIGNAL("setC"),lab)
					
					# Choix de modalité :
					if consigne == "joueur":
						option = self.choix_option()
					
						if option == "l'acheter" :  
							print "ACHAT"
					
					# Résultat de l'action : 
					res = self.rec()
					self.emit(QtCore.SIGNAL("setC"),res)
					
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~					
				elif action == "noble" :
				
					# Mise à jour de la consigne de l'action :
					lab = self.rec()
					self.emit(QtCore.SIGNAL("plateau_decliquable"))
					self.emit(QtCore.SIGNAL("setC"),lab)
					
					# Choix de modalité :
					if consigne == "joueur":
						option = self.choix_option()
						
						if option == "l'acheter" : 
							print "ACHAT"					
						
					# Résultat de l'action : 
					res = self.rec()
					self.emit(QtCore.SIGNAL("setC"),res)
					
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~					
				elif action == "fata_morgana" :
				
					# Mise à jour de la consigne de l'action :
					lab = self.rec()
					self.emit(QtCore.SIGNAL("plateau_decliquable"))
					self.emit(QtCore.SIGNAL("setC"),lab)

					# Choix de modalité :
					if consigne == "joueur":
						self.choix_option()
						option = self.rec()
						if option == "deplacerunmarqueur" :
							# Choix du marqueur :
							lab = self.rec()
							self.emit(QtCore.SIGNAL("setC"),lab)
							
							# Mise à jour des emplacements cliquables
							plateau_hi = eval(self.rec())
							self.emit(QtCore.SIGNAL("supprimer_tout_hilight"))
							self.emit(QtCore.SIGNAL("plateau_hi"),\
							[plateau_hi])
							self.emit(QtCore.SIGNAL("allow_clic"))
							
							# Boucle jusqu'à ce que le joueur clic
							self.choix_case()
							emplacement = int(self.rec())
							self.emit(QtCore.SIGNAL("supprimer_tout_hilight"))
							# Choix d'une position :
							lab = self.rec()
							self.emit(QtCore.SIGNAL("setC"),lab)
							
							# Mise à jour des emplacement cliquables
							plateau_hi = eval(self.rec())
							self.emit(QtCore.SIGNAL("supprimer_tout_hilight"))
							self.emit(QtCore.SIGNAL("plateau_hi"),\
							[plateau_hi])
							self.emit(QtCore.SIGNAL("allow_clic"))
						
							# Boucle jusqu'à ce que le joueur clic
							self.choix_case()
							destination = int(self.rec())
							self.emit(QtCore.SIGNAL("deplacer_marqueur"),[emplacement,destination])

					elif consigne == "adversaire":
						option = self.rec()
						if option == "deplacerunmarqueur":
							emplacement = int(self.rec())
							destination = int(self.rec())
							self.emit(QtCore.SIGNAL("deplacer_marqueur"),[emplacement,destination])
							
					# Résultat de l'action : 
					res = self.rec()
					self.emit(QtCore.SIGNAL("setC"),res)
					
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				elif action == "marchand" :
					
					marchand = True
					while marchand :
						# Mise à jour de la consigne de l'action :
						lab = self.rec()
						self.emit(QtCore.SIGNAL("setC"),lab)
						self.emit(QtCore.SIGNAL("plateau_decliquable"))
						# Choix de modalité :
						if consigne == "joueur":
							option = self.choix_option()
						
							if option == "rien" : marchand = False
							
							elif option == "echanger2m/1m" :
							
								# Marchandises à défausser :
								# Mise à jour de la consigne de l'action :
								lab = self.rec()
								self.emit(QtCore.SIGNAL("setC"),lab)
				
								# Choix de modalité :
								option = self.choix_option()
								
								# Marchandises en échange :
								# Mise à jour de la consigne de l'action :
								lab = self.rec()
								self.emit(QtCore.SIGNAL("setC"),lab)
				
								# Choix de modalité :
								option = self.choix_option()
	
							elif option == "echanger3m/1or" :
			
								# Marchandises à défausser :
								# Mise à jour de la consigne de l'action :
								lab = self.rec()
								self.emit(QtCore.SIGNAL("setC"),lab)
				
								# Choix de modalité :
								option = self.choix_option()
						
						else :
							choix = self.rec()
							if choix == "rien" : marchand = False


						# Résultat de l'action : 
						res = self.rec()
						self.emit(QtCore.SIGNAL("setC"),res)
						self.update_ressources()
									
												
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				elif action == "orfevre" :
				
					# Mise à jour de la consigne de l'action :
					lab = self.rec()
					self.emit(QtCore.SIGNAL("setC"),lab)
					
					# Choix de modalité :
					if consigne == "joueur":
						option = self.choix_option()
						
						if option == "echanger2m/1PV" or \
						option == "echanger4m/3PV" :
						
							# Mise à jour de la consigne de l'action :
							lab = self.rec()
							self.emit(QtCore.SIGNAL("setC"),lab)
							
							# Choix de modalité :
							option = self.choix_option()
					
					# Résultat de l'action : 
					res = self.rec()
					self.emit(QtCore.SIGNAL("setC"),res)		
					
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~					
				else : # Actions spéciales pas finie
					lab = "Action spéciale"
					self.emit(QtCore.SIGNAL("setC"),lab)
					
				#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
				# On met à jour les pions en fonction de celui utilisé
				self.emit(QtCore.SIGNAL("supprimer_pion"),case)
				
				self.update_ressources()

			self.update_pourcentage()

	#---------------------------------------------------------
	def choix_option(self):
	
		""" Fonction associée au choix d'option parmis
		celles proposées dans la consigne """
		
		while self.ui.option == "": time.sleep(0.01)
		option = self.ui.option
		self.send(str(option))
		self.ui.option = ""
		return option
		
	#---------------------------------------------------------
	def choix_case(self):
	
		""" Fonction associée au choix d'une case
		sur le plateau """
		
		while self.ui.case == 0: time.sleep(0.01)
		case = self.ui.case
		self.send(str(self.ui.case))
		self.ui.case = 0		
		return case
	#---------------------------------------------------------
	def voleur(self,info) :
	
		""" Action spéciale du voleur dans les coins """
       
		self.emit(QtCore.SIGNAL("setC"), info)
		voleur = int(self.rec())

		self.emit(QtCore.SIGNAL("voleur"),voleur)
		self.emit(QtCore.SIGNAL("plateau_hi"),[[voleur]])

		# Boucle sur le choix de l'option :
		while self.ui.option == "": time.sleep(0.01)
		option = str(self.ui.option)
		self.ui.option = ""
		self.send(option)

		res = self.rec()

		self.emit(QtCore.SIGNAL("setC"), res)

	#---------------------------------------------------------
	def fin_manche(self):
		
		""" Action associée à la fin d'une manche """
		
		self.emit(QtCore.SIGNAL("supprimer_tout_hilight"))
		

####-----------------METHODES D'ECHANGE AVEC LE SERVEUR-----------------####
	
	
	#---------------------------------------------------------
	# Fonction associé à la rception avec par défaut une réponse "ok"
	def rec(self,rep="ok"):
		m  = self.connexion.recv(1024)
		self.send(rep)
		return m
		
	#---------------------------------------------------------
	# Fonction associée à l'envoi à travers la socket principale du jeu
	def send(self,message) : 
		self.connexion.send(message)
		
	#---------------------------------------------------------
	# OPTION : 
	# Fonction pouvant être utliser pour décoder des message avec 
	# balise -> Evite de de renvoyer une réponse après chaque réception
	def decode(self,messages):
		
		return map(lambda x : x[4:], messages.split(";")[:-1])
		
	#---------------------------------------------------------
	def update_ressources(self):
	
		""" Permet de mettre à jour les ressources des deux joueurs """

		perso = self.rec()
		adv = self.rec()
		self.emit(QtCore.SIGNAL("update_ressources"),\
		[eval(perso), eval(adv)])

	#---------------------------------------------------------
	def update_pourcentage(self):
	
		""" Met à jour le pourcentage d'avancée du jeu """
		
		pourcentage = self.rec()
		self.emit(QtCore.SIGNAL("update_pourcentage"),\
		int(round(float(pourcentage))))

	#---------------------------------------------------------
	def fin_partie(self):
	
		""" Action associée à la fin de partie """
		
		fermeture()
		print "Fermeture des sockets et threads"
		
	#-----------------------------------------------------------------------------------------------------
	def gestion_tribus(self, case, consigne):
		lab = self.rec()
		self.emit(QtCore.SIGNAL("setC"),lab)
		if not lab[0]=="!":
			if consigne == "joueur":
				# Attente clic joueur
				while self.ui.option == "": time.sleep(0.01)
				self.send(str(self.ui.option))
				self.ui.option = ""
				option = self.rec()
				
				if option == "oui": # Achat tribue
					emplacements_possible = eval(self.rec())
					
					lab = self.rec()
					self.emit(QtCore.SIGNAL("setC"),lab)

					self.emit(QtCore.SIGNAL("plateau_decliquable"))
					self.emit(QtCore.SIGNAL("plateau_hi_tab"),emplacements_possible)
					self.emit(QtCore.SIGNAL("allow_clic_tab"))
		
					# Attente d'un clic sur un emplacement du tableau
					while self.ui.case_tab == -1: time.sleep(0.01)
					self.send(str(self.ui.case_tab))
					self.ui.case_tab = -1
					self.emit(QtCore.SIGNAL("plateau_decliquable_tab"))
		
					case_tab = int(self.rec())
		
					self.emit(QtCore.SIGNAL("trans_achat"),[case,case_tab,consigne])
					self.emit(QtCore.SIGNAL("change_carte_to_marchandise"),case)
				
				else: # Rien
					lab = self.rec()
					self.emit(QtCore.SIGNAL("setC"),lab)
					
			elif consigne == "adversaire":
				option = self.rec()
				if option == "oui":
					lab = self.rec()
					self.emit(QtCore.SIGNAL("setC"),lab)
					case_tab = int(self.rec())
					self.emit(QtCore.SIGNAL("trans_achat"),[case,case_tab,consigne])
					self.emit(QtCore.SIGNAL("change_carte_to_marchandise"),case)
				else :
					lab = self.rec()
					self.emit(QtCore.SIGNAL("setC"),lab)

#################################################       
class ThreadTchatEm(QtCore.QThread):
	"""objet thread gérant l'émission des messages"""
	def __init__(self, conn):
		QtCore.QThread.__init__(self)
		self.connexion = conn   # réf. du socket de connexion
		if len(sys.argv) == 2 :
			self.name = str(sys.argv[1])
		else :
			self.name = 'Client :' 
		
	def envoyer(self,message):
		try:
			message = self.name + ' : ' + message
			self.connexion.send(message)
		except:
			self.emit(QtCore.SIGNAL("fermeture"))

	def fin_partie(self):
		try:
			self.connexion.send("L'autre joueur s'est deconnecte...")
		except:
			pass
#################################################

#################################################       
class ThreadTchatRe(QtCore.QThread):
	"""objet thread gérant la reception des messages"""
	def __init__(self, conn):
		QtCore.QThread.__init__(self)
		self.connexion = conn   # réf. du socket de connexion
		
	def run(self):
		try:
			while 1:
				Message = self.connexion.recv(4096)
				self.emit(QtCore.SIGNAL("reception_message"),Message)
				time.sleep(0.1)
		except:
			self.emit(QtCore.SIGNAL("fermeture"))

#################################################

####--------Fonctions globales--------####

def fermeture():

	""" Fonction globale assurant une fermeture propre
	des threads et des sockets ouvertes pour le jeu """
	
	try:
		th_J.join()
		th_Em.join()
		th_Re.join()
		sock_jeu.close()
		sock_tchat.close()
	except :
		pass

#################################################

## Ouverture des sockets :

# Socket pour le jeu :
sock_jeu = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_jeu.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

# Socket pour le tchat :
sock_tchat = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_tchat.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

## Connexions des sockets :
try:
	sock_tchat.connect((HOST,PORT_T))
	sock_jeu.connect((HOST, PORT_J))
	
except socket.error :
    print "La connexion a échouée."
    sys.exit()
 
## Affichage fenetre graphique pour le jeu :

fen = Application(sys.argv)
fen.MainWindow = MainWindowUi(fen, PSEUDO, "Attente d'un second joueur")
ui = fen.MainWindow
tabcon = TabConnexion(PSEUDO)

## Création des threads :
th_J = ThreadJeu(sock_jeu,ui)
th_Em = ThreadTchatEm(sock_tchat)
th_Re = ThreadTchatRe(sock_tchat)

##
tabcon.connect(tabcon.but_creer,QtCore.SIGNAL("clicked()"),th_J.creer_table)
tabcon.connect(tabcon.but_joindre,QtCore.SIGNAL("clicked()"),th_J.joindre_table)
tabcon.connect(tabcon.but_rafraichir,QtCore.SIGNAL("clicked()"),th_J.rafraichir_tables)

##
th_J.connect(th_J,QtCore.SIGNAL("rafraichir_tables_joindre"),tabcon.liste_joindre.rafraichir_tables_joindre)
th_J.connect(th_J,QtCore.SIGNAL("rafraichir_parties_encours"),tabcon.tree_encours.rafraichir_parties_encours)

##
tabcon.show()

##
th_J.connect(th_J,QtCore.SIGNAL("show_game"),ui.show)
th_J.connect(th_J,QtCore.SIGNAL("close_tabcon"),tabcon.close)

## Gestions des signaux :
ui.connect(th_J,QtCore.SIGNAL("voleur"),ui.affichage_voleur)
ui.connect(th_J,QtCore.SIGNAL("plateau_hi"),ui.plateau_hi)
ui.connect(th_J,QtCore.SIGNAL("plateau_decliquable"),ui.plateau_decliquable)
ui.connect(th_J,QtCore.SIGNAL("allow_clic"),ui.allow_clic)
ui.connect(th_J,QtCore.SIGNAL("plateau_hi_tab"),ui.plateau_hi_tab)
ui.connect(th_J,QtCore.SIGNAL("allow_clic_tab"),ui.allow_clic_tab)
ui.connect(th_J,QtCore.SIGNAL("plateau_decliquable_tab"),ui.plateau_decliquable_tab)
ui.connect(th_J,QtCore.SIGNAL("cartes"),ui.modifier_carte)
ui.connect(th_J,QtCore.SIGNAL("setC"),ui.setConsignes)
ui.connect(th_J,QtCore.SIGNAL("targui"),ui.affichage_targui)
ui.connect(th_J,QtCore.SIGNAL("affichage_marqueur"),ui.affichage_marqueur)
ui.connect(th_J,QtCore.SIGNAL("supprimer_tout_hilight"),ui.supprimer_tout_hilight)
ui.connect(th_J,QtCore.SIGNAL("update_pseudo_adv"),ui.update_pseudo_adv)
ui.connect(th_J,QtCore.SIGNAL("update_couleur"),ui.update_couleur)
ui.connect(th_J,QtCore.SIGNAL("supprimer_pion"),ui.supprimer_pion)
ui.connect(th_J,QtCore.SIGNAL("update_ressources"),ui.update_ressources)
ui.connect(th_J,QtCore.SIGNAL("update_pourcentage"),ui.update_pourcentage)
ui.connect(th_J,QtCore.SIGNAL("nettoyer_cache"),ui.nettoyer_cache)
ui.connect(th_J,QtCore.SIGNAL("change_carte_to_tribu"),ui.change_carte_to_tribu)
ui.connect(th_J,QtCore.SIGNAL("change_carte_to_marchandise"),ui.change_carte_to_marchandise)
ui.connect(th_J,QtCore.SIGNAL("trans_achat"),ui.transferer_carte_achat)
ui.connect(th_J,QtCore.SIGNAL("deplacer_marqueur"),ui.deplacer_marqueur)

th_J.connect(ui,QtCore.SIGNAL("fin_jeu"),th_J.fin_partie)
th_Em.connect(ui,QtCore.SIGNAL("fin_jeu"),th_Em.fin_partie)

th_J.connect(th_J,QtCore.SIGNAL("fermeture"),fermeture)
th_Em.connect(th_Em,QtCore.SIGNAL("fermeture"),fermeture)
th_Re.connect(th_Re,QtCore.SIGNAL("fermeture"),fermeture)

th_Em.connect(ui,QtCore.SIGNAL("envoyer_message"),th_Em.envoyer)
ui.connect(th_Re,QtCore.SIGNAL("reception_message"),ui.chat_reception) # L 279

# Lancement des threads
th_J.start()
th_Em.start()
th_Re.start()

# Main loop
sys.exit(fen.exec_())
