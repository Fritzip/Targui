# -*- coding: utf-8 -*-
 
# Modules utilisées :
import random

# Fonction voleur
# Fonction décompte des points
# Fonction cases contour : OK
# Gestion pouvoir
# Gérer marchandise en stock

# Classe du jeu :

class Jeu :

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	def __init__(self) :
	
		# Initialisation des joueurs :
		
		self.blanc = { "couleur" : "Blanc", 
		"tableau" : [[],[],[]],
		 "cartes_tableau" : 0, 
		 "marchandises" : {"sel" : 2, "dattes" : 2, "poivre" : 2, "or" : 1, "pv" : 4},  
		 "carte" : [], 
		 "targuis" : [], 
		 "marqueurs" : [] }
		 
		self.bleu = {"couleur" : "Bleu",  
		"tableau" : [[],[],[]], 
		"cartes_tableau" : 0, 
		"marchandises" : {"sel" : 2, "dattes" : 2, "poivre" : 2, "or" : 1, "pv" : 4},  
		"carte" : [], 
		"targuis" : [],
		 "marqueurs" : []}
		
		self.joueurs = [self.blanc, self.bleu]
		self.positions = [6,7,8,11,12,13,16,17,18]
		# Initialisation des ressources :
		
		self.marchandises = {"sel" : 10, "dattes" : 10, "poivre" : 10, "or" : 10, "pv" : 33}
		#self.pv = 33
		
		# Initialisation des cartes :
		
		self.cartes_marchandises = [int("1%i" % i) for i in range(19)]
		random.shuffle(self.cartes_marchandises)
		
		self.cartes_marchandises_dico = {10 : [("dattes", 1)] , 
		11 : [("dattes", 1)] ,
		12 : [("sel",1)],
		13 : [("sel",1)],
		14 : [("poivre",1)],
		15 : [("poivre",1)],
		16 : [("dattes", 2)] ,
		17 : [("sel", 2)] ,
		18 : [("poivre", 2)] ,
		19 : [("poivre",1),("sel", 1)],
		110 : [("dattes", 1), ("poivre",1)],
		111 : [("sel",1),("dattes", 1)],
		
		112 : [("sel",1),("dattes", 1),("poivre", 1)],
		113 : [("sel",1),("dattes", 1),("poivre", 1)],
		114 : [("sel",1),("dattes", 1),("poivre", 1)],
		
		115 : [("or",1)],
		116 : [("or",1)],
		117 : [("or",1)],
		118 : [("pv",1)]}
		
		# ( type, coût, pv, power, num)
		self.cartes_tribus = [int("2%i" % i) for i in range(45)]
		random.shuffle(self.cartes_tribus)
		
		self.cartes_tribus_dico = {20 : ("oasis", [("poivre",1),("or",1)], 2, "", 20),
		 21 : ("oasis", [("sel",1),("dattes",1),("or",1)], 3, "",21),
		 22 : ("oasis", [("sel",1),("poivre",2),("dattes",2)], 3, "",22),
		 
		 23 : ("chameau", [("dattes",1),("sel",1),("or",1)], 3,  "",23),
		 24 : ("chameau", [("dattes",1),("poivre",1),("sel",2)], 2, "",24),
		 25 : ("chameau", [("dattes",1),("poivre",2),("sel",2)], 3, "",25),
		 
		 26 : ("puits", [("sel",1),("dattes",1),("or",1)], 3, "",26),
		 27 : ("puits", [("sel",1),("poivre",1),("dattes",2)], 2, "",27),
		 28 : ("puits", [("sel",1),("poivre",2),("dattes",2)], 3,  "",28),
		 
		 29 : ("camp", [("poivre",1),("or",1)], 2, "",29), 
		 210 :  ("camp", [("poivre",1),("dattes",1), ("or",1)], 3, "",210), 
		 211 :  ("camp", [("poivre",1),("dattes",2), ("sel",2)], 3, "",211), 
		 
		 212 : ("targia", [("dattes",1),("poivre",1),("or",1)], 3, "",212),
		 213 : ("targia", [("dattes",1),("sel",1),("poivre",2)], 2, "",213),
		 214 : ("targia", [("dattes",1),("sel",2),("poivre",2)], 3, "",214),
		 
		 215 : ("oasis", [("poivre",1),("or",1)], 1, "p1",215),
		 216 : ("chameau", [("sel",1),("or",1)], 1, "p2",216),
		 217 : ("puits", [("sel",1),("or",1)], 1, "p3",217),
		 218 : ("camp", [("dattes",1),("or",1)], 1, "p4",218),
		 219 : ("targia", [("poivre",1),("or",1)], 1, "p5",219),		
		 
		 220 : ("chameau", [("or",1)], 1, "p6",220),		
		 221 : ("camp", [("poivre",1),("dattes",1)], 1, "p7",221),		
		 222 : ("targia", [("poivre",2),("or",1)], 1, "p8",222),		
		 223 : ("chameau", [("sel",2),("dattes",2),("poivre",1)], 2, "p9",223),		
		 224 : ("chameau", [("or",1)], 1, "p10",224),		
		 225 : ("puits", [("sel",2),("dattes",1)], 1, "p11",225),	
		 
		 226 : ("camp", [("dattes",1),("poivre",2),("or",1)], 1, "p12",226),	## ressources choix
		 227 : ("targia", [("sel",2),("dattes",1),("or",1)], 1, "p13",227),		 ## ressources choix
		 
		 228 : ("oasis", [("sel",2),("dattes",1)], 1, "p14",228),
		 229 : ("oasis", [("sel",1),("poivre",1),("or",1)], 1, "p15",229),
		 
		 230 : ("camp", [("dattes",1),("or",1)], 2, "p16",230),
		 231 : ("targia", [("dattes",1),("or",1)], 1, "p17",231),
		 232 : ("puits", [("dattes",1),("or",1)], 1, "p18",232),
		 
		 233 : ("oasis", [("sel",2),("poivre",1)], 1, "p19",233),
		 234 : ("chameau", [("poivre",2),("or",1)], 2, "p20",234),
		 235 : ("targia", [("dattes",2),("or",1)], 2, "p21",235),
		 236 : ("oasis", [("dattes",1),("poivre",1),("or",1)], 2, "p22",236),
		 237 : ("puits", [("sel",2),("dattes",1),("poivre",1)], 2, "p23",237),
		 238 : ("puits", [("poivre",1),("sel",1),("or",1)], 2, "p24",238),
		 239 : ("camp", [("dattes",1),("or",1)], 1, "p25",239),
		 
		 240: ("puits", [("dattes",1),("or",1)], 1, "p26",240),
		 241 : ("targia", [("sel",1),("dattes",1),("poivre",2)], 3, "p27",241),
		 242 : ("chameau", [("dattes",2),("sel",1)], 1, "p28",242),
		 243 : ("oasis", [("sel",1),("poivre",1),("or",1)], 2, "p27",243),
		 244 : ("camp", [("sel",1),("dattes",1),("poivre",2)], 2, "p28",244) } 
		
		# oasis / camp / targia / puits / chameau	
		# Initialisation du plateau :
		
		self.voleur = 1
		self.compte_tour = 0
		self.contour = [1,2,3,5,9,10,14,15,19,21,22,23]
		
		# { case : (type) }
		self.plateau = {  0 : (0) ,  
		1 : [self.noble], 
		2 : [self.gestion_marchandises,("dattes",1)], 
		3 : [self.gestion_marchandises,("sel",1)], 
		4 : (0), 
		5 : [self.gestion_marchandises,("sel",1)], 
		6 : [1], 
		7 : [2], 
		8 : [1], 
		9 : [self.marchand], 
		10 : [self.expansion_tribale], 
		11 : [2], 
		12 : [1], 
		13 : [2], 
		14 : [self.gestion_marchandises,("poivre",1)], 
		15 : [self.caravane], 
		16 : [1], 
		17 : [2], 
		18 : [1], 
		19 : [self.gestion_marchandises,("dattes",1)] ,
		20 : (0), 
		21 : [self.gestion_marchandises,("poivre",1) ],
		22 : [self.orfevre], 
		23 : [self.fata_morgana] , 
		24 : (0) }

#------------------------------------------------------------------
	def noble(self):
		return ("noble","noble(self,joueur,j)")
	
	def marchand(self):
		return ("marchand","marchand(self,joueur,j)")
		
	def orfevre(self):
		return ("orfevre","orfevre(self,joueur,j)")
		
	def fata_morgana(self):
		return ("fata_morgana","fata_morgana(self,joueur,j)")
		
	def caravane(self):
		return ("caravane","caravane(self,joueur,j)")
		
	def expansion_tribale(self):
		return ("expansion_tribale","expansion_tribale\
		(self,joueur,j)")
			
		
#------------------------------------------------------------------	
	def initialisation_plateau(self):

		""" Placement des cartes marchandises et tribues aléatoirement en début de partie"""
		
		# liste_cartes_init = []
		for i in [6,7,8,11,12,13,16,17,18] :
		
			if self.plateau[i][0] == 1 :
				carte = self.cartes_marchandises.pop(0)
				self.plateau[i].append(carte)
				
			else :  
				carte = self.cartes_tribus.pop(0)
				self.plateau[i].append(carte)
			
	
#------------------------------------------------------------------	
	def placement_marqueur(self, joueur):

		"""Calcul de l'emplacement des marqueurs en fonction de celui des targuis"""
		
		col = []
		ligne = []
		
		for i in  joueur["targuis"] :
			if i%5 == 0 : ligne.append(i)
			elif  i%5 == 4 : ligne.append(i-4)
			else : col.append(i%5)
			
		for case_col in col :
			for case_ligne in ligne :
				
				joueur["marqueurs"].append(case_col + case_ligne)
		
		return joueur["marqueurs"]		

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def gestion_marchandises(self, (marchandise_choisie, nombre), joueur) :
	
		"""Modification du nombre de marchandises (en stock et pour joueur)"""
		
		joueur["marchandises"][marchandise_choisie] += nombre
		self.marchandises[marchandise_choisie] -= nombre	

#------------------------------------------------------------------	
	def mouvement_voleur(self) :
	
		"""Gestion des mouvements du voleur et actions spéciales (coins)"""
		
		self.liste_pos_voleur = [1,2,3,4,9,14,19,24,23,22,21,20,15,10,5,0]
		self.compte_tour += 1
		self.voleur = self.liste_pos_voleur[self.compte_tour]
		

#------------------------------------------------------------------	
	def gestion_plateau(self) :

		"""Réactualise les emplacements du contour accessibles"""
		
		self.contour = [1,2,3,5,9,10,14,15,19,21,22,23]
		self.contour.remove(self.voleur)
		return self.contour

#------------------------------------------------------------------	
	def gestion_positions(self) :
		self.positions = [6,7,8,11,12,13,16,17,18]
		for j in self.joueurs :
			for pos in j["marqueurs"] :
				self.positions.remove(pos)
	
		return self.positions		

#------------------------------------------------------------------	
	def placement_targuis(self, emp, j) :
			
		"""Placement des targuis du joueur j """
		
		self.joueurs[j%2]["targuis"].append(emp)
		return self.gestion_contour(emp)	

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def gestion_contour(self, case ) :
		
		""" Gestion des cases accessibles du contour du plateau"""
		case_face = 0
		
		self.contour.remove(case)
		
		if case%5 == 0 : case_face = case + 4
		elif case%5 == 4 : case_face = case - 4
		elif case > 20 : case_face = case - 20
		else : case_face = case + 20
		
		if case_face in self.contour : self.contour.remove(case_face)
		
		return self.contour
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def verification_ressources(self, ressources, joueur ) :
	
		"""Verification de la disponibilité de ressources fournis sous forme de liste de tuples [(marchandise, nombre), (), ()...]"""
		
		for marchandises in ressources :
			if joueur["marchandises"][marchandises[0]]\
			 - marchandises[1] < 0 : return  False
			
		return True
		
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def gestion_pv(self, pv, joueur ) :
	
		"""Gestion des modifications de points de victoire"""
		
		joueur["marchandises"]["pv"] += pv	

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def gestion_tableau(self, joueur ) :
			
		"""Détermination des emplacements disponible dans le tableau du joueur actif"""
		
		emplacements = []
		num_emplacements = []
		emplacements_possible = []
		
		for i in range(3) :
		
			if len(joueur["tableau"][i]) <4 :
				
				num_emplacements.append(i+1)
				emplacements.append("(%i) Ligne %i en position %i" % \
				(i+1, i+1, len(joueur["tableau"][i]) +1 ))
				emplacements_possible.append\
				(len(joueur["tableau"][i])+i*4)

		return num_emplacements, emplacements, emplacements_possible

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def ajout_tableau(self, emplacement, joueur, tribu ) :
				
		"""Ajout d'une carte tribu au tableau du joueur actif"""
		
		joueur["tableau"][emplacement].append(tribu[4])
		joueur["cartes_tableau"] += 1

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def mise_a_jour(self, emplacement_plateau ) :
	
		"""Mise à jour des cartes disponible au centre du plateau"""
		
		carte = self.plateau[emplacement_plateau].pop()
		
		if self.plateau[emplacement_plateau][0] == 1 : 
			self.cartes_marchandises.append(carte)
			
		self.plateau[emplacement_plateau][0] = self.plateau[emplacement_plateau][0]%2 + 1 	

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	
	def gestion_or(self, nombre, joueur) :
		
		"""Gestion des pièces d'or du joueur actif """
		
		joueur["marchandises"]["or"] += nombre	

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------									
	def remplissage_plateau(self) :
		
		"""Remplit les trous du plateau avec les cartes correspondantes"""
				
		for emplacement in [6,7,8,11,12,13,16,17,18] :
		
			if len(self.plateau[emplacement]) ==  1 :
				
				if self.plateau[emplacement][0] == 1 :
					self.plateau[emplacement].append\
					(self.cartes_marchandises.pop(0))
				else :
					self.plateau[emplacement].append\
					(self.cartes_tribus.pop(0))

#------------------------------------------------------------------									
	def phase_marqueur(self, joueur) :
		
		return joueur["targuis"] + joueur["marqueurs"]		
			
#------------------------------------------------------------------
	def fin_manche(self):
	
		""" Actions de fin de manches """
		
		self.joueurs.reverse()
		self.mouvement_voleur()
		self.remplissage_plateau()

#------------------------------------------------------------------		
	def fin_partie(self):
	
		"""Evaluation des conditions de fin de partie """
		
		return self.compte_tour == 15  or self.blanc["cartes_tableau"] == 12 or self.bleu["cartes_tableau"] == 12

#------------------------------------------------------------------
	def scores(self):

		""" Retourne les scores """
			
		# Décompte des points obtenus grâce aux tribues :
		for j in self.joueurs :
		
			type_tribue = map(lambda x : map( lambda y : self.cartes_tribus_dico[y][0], x),\
			j["tableau"] ) # On récupère le type de chaque carte.
			for ligne in type_tribue :
				if len(ligne) == 4 : # Ligne pleine
					l = list(set(ligne))
					if len(l) == 4 : j["marchandises"]["pv"] += 2 # 4 cartes différentes dans la ligne
					elif len(l) == 1 :  j["marchandises"]["pv"] += 4 # 4 cartes identiques dans la ligne
					
		# Détermination du gagnant :	
		try :  # Pas d'égalité
			return {self.joueurs[0]["marchandises"]["pv"] : "%s" % \
			self.joueurs[0]["couleur"],self.joueurs[1]["marchandises"]["pv"] : "%s" % \
			self.joueurs[1]["couleur"] }
			
		except :
			return False
						


