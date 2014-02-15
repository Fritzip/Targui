# -*- coding: utf-8 -*-

####-------FONCTIONS D'INTERACTION AVEC LE JEU-------####

#----RESUME
#																							
# - gestion_tribus -> Activation d'une carte tribu																									
# - noble -> Utilisation carte en main
# - marchand -> Echange ressources pour ressources
# - fata_morgana -> Modification emplacement marqueur
# - orfevre -> Echange ressources pour PV
# - caravane -> Pioche une carte marchandise
# - expansion_tribale -> Pioche une carte tribu
#
#--------------------

# Librairies :
import select,socket,sys,threading,time,random


##############################################################
def gestion_tribus(Partie, tribu, joueur, j ) :
	
	"""Gestion des actions associées à l'activation d'une carte tribue"""
				
	#( type, coût, pv, power, num)
	
	if Partie.jeu.verification_ressources(tribu[1], joueur)  :
	
		if joueur["cartes_tableau"] < 12 :
		
			Partie.send_dif(j,'Souhaitez-vous acheter la carte tribue "%s" sous votre marqueur (%s) pour %i pv  ? (*oui*/*non*) : ' % (tribu[0], tribu[1], tribu[2]),"%s doit choisir quoi faire de sa carte tribu"% Partie.t[j].pseudo)
			
			achat = Partie.rec(j)
			Partie.send_all(achat)
			
			if achat == "oui" : 
				
				# Paiement du coût en ressources :
				for ressources in tribu[1] : 
					Partie.jeu.gestion_marchandises((ressources[0],-ressources[1]), joueur)

				# Gain de points de victoire :
				Partie.jeu.gestion_pv(tribu[2],joueur)

				# Gestion des pouvoirs spéciales :
				# ...
	
				# Placement dans le tableau :

				lignes_dispo , emplacement_label, emplacements_possible = Partie.jeu.gestion_tableau(joueur)
	
				Partie.send(j,str(emplacements_possible))
				Partie.send_dif(j,'Où souhaitez-vous placer cette tribue "%s" ?' % tribu[0],"%s achète la tribu et doit choisir où la placer" % Partie.t[j].pseudo)
	
				emplacement = int(Partie.rec(j))
				Partie.send_all(str(emplacement))

				Partie.jeu.ajout_tableau(emplacement/4, joueur, tribu)		
				return True

			else : 
				Partie.send_dif(j,"! Vous n'achetez pas cette tribue","! %s n'achète pas cette tribue"%Partie.t[j].pseudo)
				

		else : Partie.send_dif(j,"! Vous n'avez plus de place","! %s n'a plus de place pour acheter la tribue" % Partie.t[j].pseudo)
		
	else :  Partie.send_dif(j,"! Vous n'avez pas les ressources nécessaires pour acheter cette tribue","! %s n'a pas les ressources nécessaires pour acheter la tribue" % Partie.t[j].pseudo)
	
	return False
	
##############################################################
def noble(Partie, joueur,j) :
	
	"""Action de la première tuile contour : Jouer la carte en main"""
	
	# Traitement des options possibles :
	actions_possibles = ["*ne rien faire*"]
	if len(joueur["carte"]) == 1 : 
		actions_possibles.append("*defausser la carte tribue*")
		if Partie.jeu.verification_ressources( joueur["carte"][0][1],joueur ) : actions_possibles.append("*l'acheter*")
	
	# Envoi de la consigne de l'action :
	Partie.send_dif(j, "Noble : Quelle action souhaitez-vous effectuer : %s ? " % ", ".join(actions_possibles), "Noble : %s choisit  une action " % Partie.t[j].pseudo)

	# Attente de la décision du joueur :
	choix = Partie.rec(j) # Attend la décision du joueur

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	if choix == "nerienfaire" :  # Rien
	
		res = ["Noble : Rien ce tour-ci","Noble : %s choisit de ne rien faire" % Partie.t[j].pseudo ]

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "defausserlacartetribue" : # Défausser
		Partie.jeu.cartes_tribus.append(joueur["carte"].pop())
		
		res = ["Noble : La carte que vous aviez en main a été défaussée","Noble : %s choisit de défausser sa carte en main" % Partie.t[j].pseudo ]

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "l'acheter" : # Acheter la carte
		print "ACHAT"
		#placement_tribue(Partie,joueur["carte"], joueur, j)
		#Partie.jeu.joueur["carte"].pop()
		res = ["Noble : Une nouvelle tribue est ajoutée à votre tableaux","Noble : %s a une nouvelle tribue" % Partie.t[j].pseudo]

	Partie.send_dif(j,res[0],res[1])
	
##############################################################
	
def marchand(Partie, joueur, j) :
	
	"""Action de la cinquième tuile contour"""
	marchand = True
	while marchand : # Action réalisable plusieurs fois
		# Variables locales :
		deux_marchandises = []
		trois_marchandises = []
		
		for marchandise in  ["sel","dattes","poivre"]  :
			if joueur["marchandises"][marchandise] > 1 :
				deux_marchandises.append(marchandise)
				if joueur["marchandises"][marchandise] > 2 : 
					trois_marchandises.append(marchandise)

		# Traitement des options possibles :	
		actions_possibles = ["*rien*"]
	
		# Le joueur a au moins 2 marchandises identiques :
		if len(deux_marchandises) > 0 :  
			actions_possibles.append("*echanger 2m/1m*")
			# Le joueur a au moins 4 marchandises identiques :
			if len(trois_marchandises) > 0 :
				actions_possibles.append("*echanger 3m/1or*")
			
		# Envoi de la consigne de l'action :	
		Partie.send_dif(j,"Marchand : Que souhaitez-vous faire : %s" % ", ".join(actions_possibles),"Marchand  : %s doit choisir une action à faire." % Partie.t[j].pseudo)
	
		# Attente de la décision du joueur :
		choix = Partie.rec(j)

		Partie.send(Partie.adv(j),choix)

		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		if choix == "echanger2m/1m" : 
		
			Partie.send(j,"Quelles marchandises souhaitez-vous défausser : %s ?" % ("/".join(map(lambda x : "*%s*" % x,deux_marchandises))))
				
			choix = Partie.rec(j)
			
			m = ["*sel*","*dattes*","*poivre*"]	
			Partie.send(j,"Quelles marchandise souhaitez-vous en échange : %s ?" % "/".join(m))
			
			choix2 = Partie.rec(j)
			
			Partie.jeu.gestion_marchandises((choix,-2),joueur)
			Partie.jeu.gestion_marchandises((choix2,1),joueur)
			
			res = ["Marchand : Vous récupérez 1 %s en échange de vos marchandises" % choix2,"%s gagne 1 %s" % (Partie.t[j].pseudo, choix2)]
			
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		elif choix == "echanger3m/1or" :
	
			Partie.send(j,"Quelles marchandises souhaitez-vous défausser : %s ?" % ("/".join(map(lambda x : "*%s*" % x,trois_marchandises))))
				
			choix = Partie.rec(j)
			
			Partie.jeu.gestion_marchandises((choix,-3),joueur)
			Partie.jeu.gestion_or(1,joueur)
			
			res = ["Marchand : Vous récupérez 1 or en échange de vos marchandises","%s gagne 1 or" % Partie.t[j].pseudo]
			
		#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
		elif choix == "rien" :
			res = ["Marchand : Fin de la phase marchand", "Marchand : %s a terminé la phase du marchand." % Partie.t[j].pseudo]
			
			marchand = False
		

		Partie.send_dif(j,res[0],res[1])
		Partie.update_ressources()
		
		
##############################################################
def fata_morgana(Partie,joueur,j) :
	
	"""Action de la neuvième tuile contour"""

	# Traitement des options possibles :	
	actions_possibles = ["*rien*"]
	if len(joueur["marqueurs"]) > 0 : 
		actions_possibles.append("*deplacer un marqueur*")

	# Envoi de la consigne de l'action :	
	Partie.send_dif(j,"Fata Morgana : Que souhaitez-vous \
	faire : %s ?" % ", ".join(actions_possibles),\
	"Fata Morgana : %s doit choisir quelle \
	action faire." % Partie.t[j].pseudo)

	# Attente de la décision du joueur :
	choix = Partie.rec(j)
	Partie.send_all(choix)

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	if choix == "deplacerunmarqueur" : # Déplacer
		
		# Choix du marqueur :
		Partie.send(j,"Fata Morgana : Cliquez sur le \
		marqueur à déplacer")
		
		# Emplacements cliquables
		Partie.send(j,str(joueur["marqueurs"])) 
		marqueur = int(Partie.rec(j))
		Partie.send_all(str(marqueur))
		print "marqueur = ", marqueur
		
		# Choix de l'emplacement :
		Partie.send(j,"Fata Morgana : Cliquez sur \
		l'emplacement où déplacer votre marqueur")
		
		# Emplacements cliquables
		Partie.send(j,str(Partie.jeu.gestion_positions())) 
		emplacement = int(Partie.rec(j))
		Partie.send_all(str(emplacement))

		joueur["marqueurs"].remove(marqueur)
		joueur["marqueurs"].append(emplacement)
		
		res = ["Fata Morgana : Marqueur déplacé",\
		"Fata Morgana : %s a déplacé un de ses marqueurs" \
		% Partie.t[j].pseudo]
		
		
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "rien" : # Aucune action
	
		res = ["Fata Morgana : Rien ce tour-ci",\
		"Fata Morgana : %s choisit de ne rien faire" \
		% Partie.t[j].pseudo]
	
	Partie.send_dif(j,res[0],res[1])

##############################################################
def orfevre(Partie, joueur,j) :		
	
	"""Action de la dixième tuile contour : Echange contre des points de victoire"""
	
	# Variables locales :
	deux_marchandises = []
	quatre_marchandises = []
	
	for marchandise in  ["sel","dattes","poivre"]  :
		if joueur["marchandises"][marchandise] > 1 :
			deux_marchandises.append(marchandise)
			if joueur["marchandises"][marchandise] > 3 : 
				quatre_marchandises.append(marchandise)

	# Traitement des options possibles :	
	actions_possibles  = ["*rien*"]
	
	# Le joueur a au moins 2 marchandises identiques :
	if len(deux_marchandises) > 0 :  
		actions_possibles.append("*echanger 2m/1PV*")
		# Le joueur a au moins 4 marchandises identiques :
		if len(quatre_marchandises) > 0 :
			actions_possibles.append("*echanger 4m/3PV*")
	# Le joueur a au moins 1 or :
	if joueur["marchandises"]["or"] > 0 :
		actions_possibles.append("*echanger 1or/2PV*")
		if joueur["marchandises"]["or"] > 1 :
			actions_possibles.append("*echanger 2or/4PV*")
			
	# Envoi de la consigne de l'action :	
	Partie.send_dif(j,"Orfèvre : Que souhaitez-vous faire : %s" % ", ".join(actions_possibles),"Orfèvre : %s doit choisir une action à faire." % Partie.t[j].pseudo)
	
	# Attente de la décision du joueur :
	choix = Partie.rec(j)
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	if choix == "echanger2m/1PV" : 
		
		Partie.send(j,"Orfèvre : Quelles marchandise souhaitez-vous défausser : %s ?" % ("/".join(map(lambda x : "*%s*" % x,deux_marchandises))))
		
		choix = Partie.rec(j)
		
		Partie.jeu.gestion_marchandises((choix,-2),joueur)
		Partie.jeu.gestion_pv(1,joueur)
		
		res = ["Orfèvre : Vous récupérez 1 PV en échange de vos marchandises","%s gagne 1 PV" % Partie.t[j].pseudo]
		
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "echanger4m/3PV" : 
	
		Partie.send(j,"Orfèvre : Quelles marchandise souhaitez-vous défausser : %s ?" % ("/".join(map(lambda x : "*%s*" % x,quatre_marchandises))))
		
		choix = Partie.rec(j)
		
		Partie.jeu.gestion_marchandises((choix,-4),joueur)
		Partie.jeu.gestion_pv(3,joueur)
		
		res = ["Orfèvre : Vous récupérez 3 PV en échange de vos marchandises","%s gagne 3 PV" % Partie.t[j].pseudo]
		
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "echanger1or/2PV" : 
	
		Partie.jeu.gestion_or(-1,joueur)
		Partie.jeu.gestion_pv(2,joueur)
		
		res = ["Orfèvre : Vous récupérez 2 PV en échange de votre or","%s gagne 2 PV" % Partie.t[j].pseudo]
		
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "echanger2or/4PV" : 
	
		Partie.jeu.gestion_or(-2,joueur)
		Partie.jeu.gestion_pv(4,joueur)
		
		res = ["Orfèvre : Vous récupérez 4 PV en échange de vos or","%s gagne 4 PV" % Partie.t[j].pseudo]

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "rien" :
	
		res = ["Orfèvre : Rien ce tour-ci","Orfèvre : %s choisit de ne rien faire" % Partie.t[j].pseudo]
				
	Partie.send_dif(j,res[0],res[1])
					
##############################################################
	
def caravane(Partie, joueur,j) :
	
	"""Action de la treisième tuile contour : pioche une carte marchandise"""				
	
	# Pioche la première carte de la pioche marchandise
	carte = Partie.jeu.cartes_marchandises.pop(0)
	for marchandise in Partie.jeu.cartes_marchandises_dico[carte] :
		Partie.jeu.gestion_marchandises(marchandise, joueur)
	
	# Remet la carte dans la pioche
	Partie.jeu.cartes_marchandises.append(carte)
	
	# Envoi du résultat de l'action
	Partie.send_dif(j,"Caravane : Vous avez pioché %s" % \
	Partie.jeu.cartes_marchandises_dico[carte],\
	"Caravane :  %s a pioché la carte marchandise  %s" % \
	(Partie.t[j].pseudo, \
	Partie.jeu.cartes_marchandises_dico[carte][0]))
	
##############################################################

def expansion_tribale(Partie, joueur,j) :
	
	"""Action de la quatorsième tuile contour : Piocher une carte tribue"""	

	# Pioche la première carte tribue
	carte = Partie.jeu.cartes_tribus.pop(0) 
	# Récupère info sur la carte
	carte_info = Partie.jeu.cartes_tribus_dico[carte]  
	
	# Traitement des options possibles :
	actions_possibles = ["*defausser la carte piochee*"]
	if len(joueur["carte"]) == 0 : 
		actions_possibles.append("*la conserver en main*")
	if Partie.jeu.verification_ressources(Partie.jeu.cartes_tribus_dico[carte][1], joueur)and joueur["cartes_tableau"] < 12 : 
		actions_possibles.append("*l'acheter*")
	
	# Envoi des consignes :
	Partie.send_dif(j, "Expansion tribale : Vous avez pioché une carte (%s) de coût (%s) rapportant %i PV. Que souhaitez-vous en faire : %s" % (carte_info[0], carte_info[1], carte_info[2],", ".join(actions_possibles)), "Expansion tribale : %s choisit quoi faire de la carte piochée." % Partie.t[j].pseudo)
	
	# Attente de la décision du joueur :
	choix = Partie.rec(j) 	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	if choix == "laconserverenmain" : # Conserver en main
		joueur["carte"].append(carte_info)
			
		res = ["Expansion tribale : La tribue est ajoutée à votre main", "Expansion tribale : %s choisit de conserver la tribue dans sa main" % Partie.t[j].pseudo ]

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "l'acheter" : # Acheter
	
		print "ACHAT"	
		
		res = ["Expansion tribale : Une nouvelle tribue est ajoutée à votre tableaux", "Expansion tribale : %s a une nouvelle tribue" % Partie.t[j].pseudo]
		
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	elif choix == "defausserlacartepiochee" : # Défausser
	
		Partie.jeu.cartes_tribus.append(carte)
		res = ["Expansion tribale : Cette carte tribue a été défausser","Expansion tribale : %s a défausser la carte tribue piochée." % Partie.t[j].pseudo ]
		
	Partie.send_dif(j,res[0],res[1])
	

