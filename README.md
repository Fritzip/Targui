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

<ol>
<li><p>Lancer le serveur : </p>

<p><code>python serveur_targui.py [-ip ip] [-pj port_jeu] [-pt port_tchat]</code></p></li>
<li><p>Lancer un client : </p>

<p><code>python client_targui.py -n nom [-ip ip] [-pj port_jeu] [-pt port_tchat]</code></p>

<p>Sans paramètres, utilisation des valeurs par défaut : (127.0.0.1 ; 8012 ; 8021). Le pseudo sera malgré tout demandé.</p></li>
<li><p>Dans la fenêtre qui s'ouvre choisir:</p>

<ul>
<li>[créer]       une nouvelle table et attendre un autre joueur </li>
<li>[joindre]     une table déjà existante (ou double-clic) </li>
<li>[rafraichir]  permet de voir l'évolution des parties et éventuellement les nouvelles tables créées.</li>
</ul></li>
<li><p>Une fois la partie lancée, suivre les instructions qui s'affiche en haut à gauche de la fênetre du jeu.</p></li>
<li><p>Dès qu'un des joueurs ferme cette fenêtre graphique la partie est arrêté.</p></li>
</ol>

### Codes Couleurs ###

Les emplacements rouges sont les emplacements cliquables et les emplacements gris ou bleu correspondent aux joueurs. Une petite pastille à côté de votre pseudo permet de connaître votre couleur.

### Crédits ###

Emma Prudent & Maxime Sainlot

4BIM - INSA Lyon - Projet Réseau

_Bon Jeu_