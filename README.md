# Targui #

### Fichiers ###

Le projet est divisé en plusieurs fichiers :

* serveur_targui.py
* client_targui.py
* targui_jeu_gui.py
* tab_connexion.py
* targui_gui.py

### Dépendances ###

Les librairies de base de `Python v2.7`:

* select
* socket
* sys
* threading
* time
* random
* copy 

La librairie graphique :

* PyQt4 _(nécessite une installation)_


### Lancement du programme ###


* Lancer le serveur : 

	```bash
	python serveur_targui.py [-ip ip] [-pj port_jeu] [-pt port_tchat]
	```

* Lancer un client : 

	```bash
	python client_targui.py -n nom [-ip ip] [-pj port_jeu] [-pt port_tchat]`
	```

	Sans paramètres, utilisation des valeurs par défaut : (127.0.0.1 ; 8012 ; 8021). Le pseudo sera malgré tout demandé.

* Dans la fenêtre qui s'ouvre choisir:

	* [créer] une nouvelle table et attendre un autre joueur 
	* [joindre]	une table déjà existante (ou double-clic) 
	* [rafraichir] l'affichage, permet de voir l'évolution des parties et éventuellement les nouvelles tables créées.
	
* Une fois la partie lancée, suivre les instructions qui s'affiche en haut à gauche de la fênetre du jeu.

* Dès qu'un des joueurs ferme cette fenêtre graphique la partie est arrêté.

### Codes Couleurs ###

Les emplacements rouges sont les emplacements cliquables et les emplacements gris ou bleu correspondent aux joueurs. Une petite pastille à côté de votre pseudo permet de connaître votre couleur.

### Crédits ###

Emma Prudent & Maxime Sainlot

4BIM - INSA Lyon - Projet Réseau

_Bon Jeu_