# -*- coding: utf-8 -*-

####-------SERVEUR du jeu TARGUI-------####

#----RESUME
#																							
# - ThreadServeur(soket_serveur) -> En écoute sur le réseau							 
# - ThreadClient(socket_serveur) -> Gestion des nouveaux clients						
# - ThreadPartie(socket_serveur) -> Gestion des parties								
#																					
# - ThreadTchatRec(socket_tchat) -> Reçoit les messages instantanés des clients
# - ThreadTchatEm(socket_tchat) -> Transmet les messages des clients	
#
#--------------------

#---------------------------------------------------------------------------------

# MISSIONS :
# Mettre à jour plateau phase voleur (position voleur et plus de highlight + ressources)
# Si on clic trop vite pour retirer ses targuis/marqueurs => erreur
# Visualiser carte en main + défausser
# Mettre à jour label une fois tribu achetée


# Librairies :
import select,socket,sys,threading, time,random

# Autres fichiers :
from targui_gui import *
from targui_jeu_gui import * 
from fonctions_jeu import * 

## Variables globales ##
NOMBREJOUEUR = 2
TABLES = {}
PARTIES = {}

HOST = '' # on écoute tout
PORT_J = 8012 # Pour le jeu
PORT_T = 8021 # Pour le tchat
BACKLOG= 5
SIZE= 1024
THREADS = []
LISTEN = 2
RAPPORT_AV = 100/60.

# Usage python serveur_targui.py [-ip ip] [-pj port_jeu] [-pt port_tchat]
if len(sys.argv)>1:
	for i in range(len(sys.argv)):
		if sys.argv[i]=='-ip':
			HOST=str(sys.argv[i+1])
		elif sys.argv[i]=='-pj':
			PORT_J= int(sys.argv[i+1])
		elif sys.argv[i]=='-pt':
			PORT_T= int(sys.argv[i+1])

################################################################
class ThreadServeur(threading.Thread):
	
	""" Thread en écoute sur le réseau pour la connexion de nouveau clients"""
	
	#----------------------------------------------------------
	def __init__(self, socket_jeu, socket_tchat):
		
		threading.Thread.__init__(self)
		self.socket_jeu = socket_jeu
		self.socket_tchat = socket_tchat 
		
	#----------------------------------------------------------
	def run(self):
				
		print "Serveur mis en route - Attente de connexions"
		try:
			while True :
				tchat_c = self.socket_tchat.accept()
				c = Thread_Client(self.socket_jeu.accept(),tchat_c)
				c.start()
		except:
			self.socket_tchat.close()
			self.socket_jeu.close()
						
################################################################
class Thread_Client(threading.Thread) :
	
	""" Thread de gestion des nouveaux clients
	Assignation à des tables de jeu + Lancement des parties """

	#---------------------------------------------------------
	def __init__(self, (sock_client, address), (socket_tchat ,adrress2)):
		
		### Phase 0 - Initialisation des clients :
		
		threading.Thread.__init__(self)
		self.sock_client = sock_client
		self.sock_tchat = socket_tchat
		
		# Initialisés plus tard :
		self.pseudo = ""
		self.couleur = ""
		
	#----------------------------------------------------------	
	def run(self):
	
		global TABLES, PARTIES

		try:
			### Phase 0 - Choix pseudos :
			
			pseudo = self.sock_client.recv(1024)
			self.pseudo = pseudo
			
			### Phase 0 - Choix d'une table :
			
			# Déclenche la phase de choix de table pour le client
			while True:
				self.send("choix_table")	
				(tables_dispo,choix) = self.rafraichir()
				
				# On attend la réponse du client
				choix = self.sock_client.recv(1024)
				if choix.upper() == "N" :
					self.send("attente")
					TABLES[len(TABLES)+1] = [self]
					break
					
				elif choix in tables_dispo :
					self.send("attente")	
					
					# On ajoute le client à une table existante
					TABLES[int(choix)].append(self)
				
					# On lance une partie sur cette table
					partie = ThreadPartie(self.sock_client,TABLES[int(choix)],int(choix))
					partie.start()
					PARTIES[int(choix)] = partie

					del TABLES[int(choix)]
					break
					
				elif choix.upper() == 'R':
					pass
					
		except:
			self.sock_client.close()	

	#----------------------------------------------------------
	def rafraichir(self):
	
		"""Permet le rafraichissement des tables et parties"""
		
		# Au moins une table en attente sur le serveur :
		tables_dispo = []
		choix = []
		for table in TABLES.keys():
			if len(TABLES[table])<2 :
				choix.append([str(table),str(TABLES[table][0].pseudo)])
				tables_dispo.append(str(table))

		# On envoi la liste des choix possibles
		self.send("%s" % choix)
	
		# Envoi des parties en cours pour suivre la progression :
		l = map(lambda x : '["%s & %s","2/2","%i %%","%i min %isec"]' % (x.t[0].pseudo,x.t[1].pseudo,x.pourcentage*RAPPORT_AV, (time.time()-x.temps)/60,(time.time()-x.temps)%60),PARTIES.values())
		 
		self.send(str(l))
		 
		return (tables_dispo,choix)
		
	#----------------------------------------------------------
	def send(self,message):
	
		""" Envoi un message et attend une réponse au client """
		
		self.sock_client.send(message)
		ack = self.sock_client.recv(1024)
		
################################################################
class ThreadPartie(threading.Thread):
	
	""" Thread associée au déroulement d'une partie du jeu"""
	
	#----------------------------------------------------------
	def __init__(self, conn, joueurs, num_partie):
		
		threading.Thread.__init__(self)
		self.connexion = conn   # réf. du socket de connexion
		
		## Initialisation jeu :
		self.jeu = Jeu()
		self.t = joueurs # instance des clients
		self.pourcentage = 0
		self.joueurs = {}
		self.temps = time.time()
		self.num = num_partie
		
		## Lancement du tchat pour la table
		self.Tchat = ThreadTchat(self.t[0].sock_tchat,self.t[1].sock_tchat)
		self.Tchat.start()
		
	#----------------------------------------------------------
	def run(self):
		
		#------------------------#
		# Début partie   #
		#------------------------#
				
		try : 
					
			# Phase 0 - Début du jeu :
			#---------------------------------------

			# Permet d'avertir les clients du début de la partie :
			self.send_all("start") 
		
			# Random ordre de jeu (Premier joueur en position 0)
			random.shuffle(self.t) 
		
			for i in range(2) : 
				self.t[i].couleur = self.jeu.joueurs[i]["couleur"] # Initalisation des couleurs 
				self.joueurs[self.t[i].couleur] =  self.t[i].pseudo # Association pseudo/couleur
				self.send(i,self.t[i].couleur) # Envoi de sa couleur
				self.send(i,self.t[self.adv(i)].pseudo) # Pseudo de l'adversaire

			# Initialisation du plateau de départ :
			self.init_plateau()

			#--------------------------------------------------------#
			# Boucle jusqu'à la fin de la partie   #
			#--------------------------------------------------------#
					
			while True:
				if not self.jeu.fin_partie():
					if self.jeu.compte_tour in [3,7,11] : 
						self.voleur(self.jeu.compte_tour)
						self.jeu.mouvement_voleur()
				
					self.send_all("go")
					self.update_plateau()
					self.phase1()
					self.phase2()
					self.phase3()
					self.fin_manche()
				else : 
					if self.jeu.compte_tour == 15 : self.voleur(self.jeu.compte_tour)
					self.send_all("break")				
					self.send_all(self.fin_partie())
					break
			
			self.fermeture()
			
		except:
			print "FIN PARTIE"
			self.fermeture()


#####--------------------PHASES DU JEU--------------------------------------------------------------####

	def fermeture(self):

		""" Fonction permettant de fermer une partie en cours """

		print "FERMETURE"
		global PARTIES

		# Fermeture du tchat
		self.Tchat._Thread__stop() 

		# Fermeture des sockets jeu des clients
		self.t[0].sock_client.close() 
		self.t[1].sock_client.close()

		# Fermeture des sockets tchat des clients
		self.t[0].sock_tchat.close()
		self.t[1].sock_tchat.close() 

		# Fermeture socket de connexion :
		self.connexion.close() 

		# Suppression de la partie des parties en cours :
		del PARTIES[int(self.num)] 
		# Suppression de la partie des parties en cours :

	#----------------------------------------------------------
	def phase1(self):
	
		""" Phase I : Placement des targuis """
		
		for j in range(6) :  
	
			## Messages différents à chaque joueurs :
			self.send_dif( j%2, "Placer un targui sur une carte du contour","C'est au tour de %s" % self.t[j%2].pseudo )

			## Consigne joueur/non joueurs :
			self.send_dif(j%2, "go", "wait")

			## Reception de la case cliquée par le joueur actif :
			case = self.rec(j%2)

			# Envoie des nouvelles données à tous les joueurs
			self.send_all(str(self.jeu.placement_targuis(int(case),j%2)))
			self.send_all(str(case))
			self.send_all(str(self.jeu.joueurs[j%2]["couleur"].lower()))
			
		self.update_pourcentage()

	#----------------------------------------------------------
	def phase2(self):
	
		""" Phase II : Placement des marqueurs """

		# Calcul et placement des marqueurs :
		l_marqueurs = []
		for joueur in self.jeu.joueurs : 
			for marqueur in self.jeu.placement_marqueur(joueur) : 
				l_marqueurs.append([joueur["couleur"].lower(),marqueur])

		# Envoi ces informations à tous les joueurs :
		self.send_all(str(l_marqueurs))
		self.jeu.gestion_positions()
		
	#----------------------------------------------------------
	def phase3(self):
	
		""" Phase III : Récupération des pions """

		self.update_pourcentage()
		
		# Les joueurs récupère chacun leur tour leur pions.
		for j in range(2) :
			joueur = self.jeu.joueurs[j]
			self.send_dif( j, "Retirez vos pions.", "C'est au tour de %s." % self.t[j].pseudo)
			self.send_dif(j, "joueur", "adversaire")

			while True :
			
				# Tous les pions ont été récupérés
				if len(self.jeu.phase_marqueur(joueur)) == 0 :
					self.send_all("break")				
					break
					
				# Sinon le joueur continu à retirer ses pions
				else : self.send_all("go on")
				
				# Envoi la couleur du joueur et les cases cliquables
				self.send_all(joueur["couleur"].lower())
				self.send_all(str(self.jeu.phase_marqueur(joueur)))
				
				# On récupère la case cliquée que l'on communique à
				# tous les clients
				case = self.rec(j)
				self.send_all(case)
				case = int(case)

				# Actions targuis :
				if case in joueur["targuis"] :
				
					# Marchandises :
					if len(self.jeu.plateau[case]) > 1 : 
						self.jeu.plateau[case][0](self.jeu.plateau[case][1], joueur) 
						self.send_all("marchandise_targui")
						self.send_dif(j,"Vous gagnez +1 %s" % self.jeu.plateau[case][1][0],\
						"%s gagne +1 %s"%(self.t[j].pseudo,self.jeu.plateau[case][1][0]))
						
					# Actions spéciales :
					else :
						action = self.jeu.plateau[case][0]()
						print "action spéciale ", action[0]
						self.send_all(action[0])
						eval(action[1])
				
					joueur["targuis"].remove(case)

				# Action marqueurs :
				elif case in joueur["marqueurs"]  : 
		
					if self.jeu.plateau[case][0] == 1 : 
					
						# Marchandises
						lab = ""
						for i in self.jeu.cartes_marchandises_dico[self.jeu.plateau[case][1]] : 
							self.jeu.gestion_marchandises(i, joueur) 
							lab += " +%i %s"%(int(i[1]),i[0])
						
						self.send_all("marchandise_marqueur")
						self.send_dif(j,"Vous gagnez %s"%lab,"%s gagne %s"%(self.t[j].pseudo,lab))
						
						self.jeu.mise_a_jour(case)			
				
					else :
					
						# Tribues
						self.send_all("tribus_marqueur")
						# Si l'action conduit à l'achat de la carte
						if gestion_tribus(self,self.jeu.cartes_tribus_dico[self.jeu.plateau[case][1]], joueur,j):
							self.jeu.mise_a_jour(case)
						
						# Sinon cette position est de nouveau libre
						else : self.jeu.positions.append(case)
						
					joueur["marqueurs"].remove(case)	

				self.update_ressources()
			self.update_pourcentage()
					
#####--------------------FONCTIONS DU JEU------------------------------------------------------####

	#----------------------------------------------------------
	def init_plateau(self):
	
		"""Initialise le plateau au début du jeu """
		
		self.jeu.initialisation_plateau()

	#----------------------------------------------------------
	def update_plateau(self) :
	
		""" Met à jour l'affichage du plateau de jeu """
		
		cartes = []
		for i in [6,7,8,11,12,13,16,17,18] :
			if self.jeu.plateau[i][0] == 1 :
				cartes.append((i,self.jeu.plateau[i][1],"marchandise"))
				
			else :  
				cartes.append((i,self.jeu.plateau[i][1], \
				self.jeu.cartes_tribus_dico\
				[self.jeu.plateau[i][1]][0]))

		# Découverte des cartes initiales
		e = self.send_all(str(cartes)) 
		
		# Préparation des emplacements cliquables
		e = self.send_all(str(self.jeu.gestion_plateau())) 
		
		# Position initiale du voleur
		e = self.send_all(str(self.jeu.voleur)) 
		
		# Ressources initiales
		self.update_ressources()
		self.update_pourcentage()

	#----------------------------------------------------------
	def update_ressources(self):
	
		"""Mise à jour des ressources """
		i = 0
		self.send_dif(i,str(self.jeu.joueurs[i]["marchandises"]),\
		str(self.jeu.joueurs[(i+1)%2]["marchandises"]))
		
		self.send_dif(i,str(self.jeu.joueurs[(i+1)%2]\
		["marchandises"]),str(self.jeu.joueurs[i]["marchandises"]))

	#----------------------------------------------------------
	def update_pourcentage(self):
	
		""" Mise à jour des pourcentages de progression de partie"""
		
		self.pourcentage += 1
		self.send_all(str(self.pourcentage*RAPPORT_AV))

	#----------------------------------------------------------
	def voleur(self,tour):
	
		""" Action spéciale du voleur dans les coins """
		
		if tour == 3 : t = (1,1)
		elif tour == 7 : t = (2,1)
		elif tour == 11 : t = (3,2)
		elif tour == 15 : t = (1,3)
		
		if tour != 15 : v = "marchandise"
		else : v = "piece d'or"

		consigne = "Le voleur fait des siennes mais il vous laisse choisir ce qu'il vous vole :*%i %s* ou *%i point(s) de victoire* ?" % (t[0],v,t[1])
		self.send_all(consigne)
		self.send_all(str(self.jeu.voleur))

            
		for j in range(2) :
			choix = self.rec(j)
			if choix == "%i%s" % (t[0],v)  :
            
				if tour != 15 :
					# Suppression marchandises :
					m_dispo= []
					for i in ["sel","dattes","poivre"]:
						for march in range(self.jeu.joueurs[j]["marchandises"][i]) :
							m_dispo.append(i)
                        
					if len(m_dispo) >= t[0] :
						m_volees = random.sample(m_dispo,t[0] )
					else : m_volees = m_dispo
                    
					if m_volees == [] :
						consigne = "Le voleur a bien cherché, mais vous n'avez aucune marchandise, vous lui échappez cette fois-ci."
                        
					else :
						for m in m_volees :
							self.jeu.gestion_marchandises((m,-1),self.jeu.joueurs[j])
                    
						consigne = "Le voleur vous a volé : %s" % m_volees
                    
				else :
					# Suppresion pièce d'or :
					self.jeu.gestion_or(-t[0],self.jeu.joueurs[j])
					consigne = "Le voleur vous a volé %i pièce d'or" % t[0]
                    
			elif choix == "%ipoint(s)devictoire" % t[1] :
				self.jeu.gestion_pv(-t[1],self.jeu.joueurs[j])
				consigne = "Le voleur vous a volé %i points de victoire" % t[1]
            
            
			self.send(j,consigne)
				
	#----------------------------------------------------------
	def fin_manche(self):
		
		""" Actions de fin de manche """
		
		self.t.reverse() # On change le premier joueur
		self.jeu.fin_manche()

	#----------------------------------------------------------
	def fin_partie(self):
		
		"""	Actions de fin de partie """
		
		s = self.jeu.scores() # score
	
		if s :
			mes = "1er : %s (PV = %i)\n2ème : %s (PV = %i)" % (self.joueurs[s[max(s.keys())]], max(s.keys()),self.joueurs[s[min(s.keys())]], min(s.keys()))
			
		else :
			mes = "Bravo, aujourd'hui pas de perdant ! Vous êtes à égalité"

		return mes	
			

#####--------------------FONCTIONS D'ECHANGE RESEAU---------------------------------####
	
	#----------------------------------------------------------
	# Renvoie l'adversaire du joueur considéré :
	def adv(self, joueur) : return (joueur+1)%2

	#----------------------------------------------------------
	# Permet de recevoir des messages des joueurs :
	def rec(self, joueur) :
		return self.t[joueur].sock_client.recv(4096)

	#----------------------------------------------------------
	# Permet d'envoyer un message à un joueur en attendant 
	# sa réponse
	def send(self, joueur, message) :
		self.t[joueur].sock_client.send(message)
		a = self.t[joueur].sock_client.recv(4096)

	#----------------------------------------------------------
	# Permet d'envoyer un même message à tous les joueurs en
	# attendant leurs réponses
	def send_all(self, message):
		
		for client in self.t :	
			client.sock_client.send(message)
			a = client.sock_client.recv(4096)			
		return True

	#----------------------------------------------------------
	# Permet d'envoyer un message différents aux deux joueurs 
	# en attendant leurs réponses
	def send_dif(self, joueur, message_joueur, message_adv):
	
		self.t[joueur].sock_client.send(message_joueur)
		a = self.t[joueur].sock_client.recv(4096)
		self.t[self.adv(joueur)].sock_client.send(message_adv)
		a = self.t[self.adv(joueur)].sock_client.recv(4096)

########################################################
class ThreadTchat(threading.Thread):
	
	""" Thread permettant de gérer en parallèle un tchat 
	entre les joueurs d'une même table de jeu"""
		   
	#----------------------------------------------------------
	def __init__(self, socket_c1,socket_c2):
		
		""" Initialisation et prise en considération des sockets
		mises en place pour le tchat pour les clients considérés """
		
		threading.Thread.__init__(self)
		self.sockets = [socket_c1,socket_c2] # sockets client
		
	#----------------------------------------------------------
	def diffuser_msg(self,message):
		
		""" Fonction pour diffuser les messages a tous les clients """
		
		for socket in self.sockets :
			try :
				socket.send(message)
			except :
				pass

	#----------------------------------------------------------
	def run(self):
		
		""" Fonction principale permettant de récupérer
		les sockets qui envoie sur le réseau et leur message
		pour le transmettre aux joueurs de la table """
		
		try:
			while True:
				read_sockets,write_sockets,error_sockets = select.select(self.sockets,[],[])
				for sock in read_sockets:
					Message = sock.recv(4096)
					self.diffuser_msg(Message)               			
		except :
			pass
			
				        

#################################################

## Ouverture des sockets :

try :
	# Ouverture d'une socket pour le jeu
	sock_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_serveur.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	sock_serveur.bind( (HOST, PORT_J) )
	sock_serveur.listen(LISTEN)

	# Ouverture d'une socket pour le tchat
	sock_tchat =  socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock_tchat.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	sock_tchat.bind( (HOST, PORT_T) )
	sock_tchat.listen(LISTEN)
	
except socket.error, (value, message):	
	if sock_serveur : sock_serveur.close()
	print "(S) Ouverture impossible des sockets :" + message
	sys.exit(1)			

## Création et lancement de la thread serveur :
th_serv = ThreadServeur(sock_serveur,sock_tchat)
th_serv.start()
