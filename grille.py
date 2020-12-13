# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 21:01:59 2020

@author: arian
"""
import random
import time
import numpy as np
import gurobipy as gp
import tkinter as tk
from collections import defaultdict

class Grille():
    """
    Représente la grille. 
    La grille est représentée par un array numpy 2D d’entiers, chaque entier 
    représentant une couleur. 
    Initialise la grille des couleurs de façon aléatoire et contient une 
    méthode pour initialiser des poids de façon aussi aléatoire dans une 
    deuxième grille auxiliaire.
    
    Parameters
    ----------
    nb_lig : int
        Nombre de lignes de la grille.
    nb_col : int
        Nombre de colonnes de la grille.
    tab_cost : list(int)
        Liste des coûts de chaque couleur. Sa taille doit être égale au 
        paramètre couleurs. Le défaut est [1, 2, 3, 4].
    p : float
        Probabilité d’atteindre la case cible. Le défault vaut 1.
    proba_coul : list(float)
        Liste des probabilités pour l'occurrence de chaque couleur 
        (taille égale à la quantité de couleurs) si None, probabilité uniforme.
        Le défaut est None.
    proba_mur : float
        Probabilité d'occurrence des murs. Le défaut vaut 0.
    proba_nb : list(float)
            Liste des probabilités pour l'occurrence de chaque chiffre entre 1 
            et 9. Si None, probabilité uniforme. Le défault est None.
        
    Attributes
    ----------
    tab : numpy.ndarray
        Tableau représentant la grille. Chaque case contient un nombre 
        indiquant à quelle couleur la case est associée. Les cases avec -1 
        contiennent des murs.
    tab_cost : list(int)
        Liste des coûts de chaque couleur.
    p : float
        Probabilité d’atteindre la case cible.
    chiffre : numpy.ndarray
        Tableau représentant les prix de la grille. Chaque case contient un 
        chiffre entre 1 et 9.
    """
    
    def __init__(self, nb_lig, nb_col, tab_cost = [1, 2, 3, 4], p = 1, proba_coul = None, proba_mur = 0, proba_nb = None):
        couleurs = len(tab_cost)
        #On confirme que les tailles sont bonnes
        assert (proba_coul is None) or (len(proba_coul) == couleurs), "Tableau des probabilités des couleurs avec la mauvaise taille"   
        
        #On calcule les probabilités des couleurs et murs (les probas des couleurs sont conditionnelles au début)
        proba_tab = np.empty(couleurs + 1)
        proba_tab[0] = proba_mur
        proba_tab[1:] = proba_coul or (np.ones(couleurs) / couleurs)
        proba_tab[1:] *= (1 - proba_mur)  
        #Création de la grille
        self.tab = np.random.choice(couleurs + 1, (nb_lig, nb_col), p = proba_tab) - 1
        self.tab_cost = tab_cost
        self.p = p
        self.chiffre = np.random.choice(9, self.tab.shape, p = proba_nb) + 1
        

    def proba_trans(self, i, j, action):
        """
        Calcule les cases atteignables a partir d’une case (i, j) quelconque en
        prenant l’action a, et les respectives probabilités.
        
        Parameters
        ----------
        i : int
            Indice de ligne de la case.
        j : int
            Indice de colonne de la case.
        a : int
            L’action à réaliser. L’encodage est 0-haut, 1-droite, 2-bas,
            3-gauche.
            
        Attributes
        ----------
        cases_p : defaultdict((int, int), float)
            Dictionnaire indexé par les cases atteignables et contenant les 
            probabilités d’atteindre chaque case.
        """
        
        cases_p = defaultdict(lambda: 0)
        # On teste si la case cible est atteignable et après on calcule leur 
        # voisinage dans le cas positif. Dans le cas negatif, on reste sur la
        # case passé en argument.
        if action == 0 and self.case_possible(i - 1, j):
            case_droite = int(self.case_possible(i - 1, j + 1))
            case_gauche = int(self.case_possible(i - 1, j - 1))
            cases_p[(i - 1, j)] = self.p
            cases_p[(i - 1, j - case_gauche)] += (1 - self.p) / 2
            cases_p[(i - 1, j + case_droite)] += (1 - self.p) / 2
            
        elif action == 1 and self.case_possible(i, j + 1):
            case_bas = int(self.case_possible(i + 1, j + 1))
            case_haut = int(self.case_possible(i - 1, j + 1))
            cases_p[(i, j + 1)] = self.p
            cases_p[(i - case_haut, j + 1)] += (1 - self.p) / 2
            cases_p[(i + case_bas, j + 1)] += (1 - self.p) / 2

        elif action == 2 and self.case_possible(i + 1, j):
            case_droite = int(self.case_possible(i + 1, j + 1))
            case_gauche = int(self.case_possible(i + 1, j - 1))
            cases_p[(i + 1, j)] = self.p
            cases_p[(i + 1, j - case_gauche)] += (1 - self.p) / 2
            cases_p[(i + 1, j + case_droite)] += (1 - self.p) / 2

        elif action == 3 and self.case_possible(i, j - 1):
            case_bas = int(self.case_possible(i + 1, j - 1))
            case_haut = int(self.case_possible(i - 1, j - 1))
            cases_p[(i, j - 1)] = self.p
            cases_p[(i - case_haut, j - 1)] += (1 - self.p) / 2
            cases_p[(i + case_bas, j - 1)] += (1 - self.p) / 2

        else:
            cases_p[(i, j)] = 1

        return cases_p
    
    def proba_trans_arr(self, i, j):
        arr = {}
        if self.case_possible(i - 1, j - 1):
            if self.case_possible(i - 1, j):
                arr[i - 1, j - 1, 1] = (1 - self.p)/2
            if self.case_possible(i, j - 1):
                arr[i - 1, j - 1, 2] = (1 - self.p)/2
                
        if self.case_possible(i - 1, j + 1):
            if self.case_possible(i - 1, j):
                arr[i - 1, j + 1, 3] = (1 - self.p)/2
            if self.case_possible(i, j + 1):
                arr[i - 1, j + 1, 2] = (1 - self.p)/2    
                
        if self.case_possible(i + 1, j + 1):
            if self.case_possible(i, j + 1):
                arr[i + 1, j + 1, 0] = (1 - self.p)/2
            if self.case_possible(i + 1, j):
                arr[i + 1, j + 1, 3] = (1 - self.p)/2
                
        if self.case_possible(i + 1, j - 1):
            if self.case_possible(i, j - 1):
                arr[i + 1, j - 1, 0] = (1 - self.p)/2
            if self.case_possible(i + 1, j):
                arr[i + 1, j - 1, 1] = (1 - self.p)/2
                
        if self.case_possible(i - 1, j):
            arr[i - 1, j, 2] = self.p
            if not self.case_possible(i, j - 1):
                arr[i - 1, j, 2] += (1 - self.p)/2
            if not self.case_possible(i, j + 1):
                arr[i - 1, j, 2] += (1 - self.p)/2
        else:
            arr[i, j, 0] = 1        
        
        if self.case_possible(i, j + 1):
            arr[i, j + 1, 3] = self.p
            if not self.case_possible(i - 1, j):
                arr[i, j + 1, 3] += (1 - self.p)/2
            if not self.case_possible(i + 1, j):
                arr[i, j + 1, 3] += (1 - self.p)/2
        else:
            arr[i, j, 1] = 1 
                
        if self.case_possible(i + 1, j):
            arr[i + 1, j, 0] = self.p
            if not self.case_possible(i, j - 1):
                arr[i + 1, j, 0] += (1 - self.p)/2
            if not self.case_possible(i, j + 1):
                arr[i + 1, j, 0] += (1 - self.p)/2
        else:
            arr[i, j, 2] = 1 
                
        if self.case_possible(i, j - 1):
            arr[i, j - 1, 1] = self.p
            if not self.case_possible(i - 1, j):
                arr[i, j - 1, 1] += (1 - self.p)/2
            if not self.case_possible(i + 1, j):
                arr[i, j - 1, 1] += (1 - self.p)/2
        else:
            arr[i, j, 3] = 1
            
        return arr
        
    def case_possible(self, i, j):
        return i >= 0 and j >= 0 and i < self.tab.shape[0] and j < self.tab.shape[1] and self.tab[i, j] >= 0
      
    def case_cout(self, i, j, mode):
        if mode == "couleur":
            return self.tab_cost[self.tab[i, j]]
        elif mode == "somme_chiffre":
            return self.chiffre[i, j]
            
         
class Visualisation():
    """
    Classe créée pour faciliter la visualisation des grilles et la 
    movimentation du robot.
    Permet la visualisation des deux types de grille avec un guidage manuel du 
    robot par les flèches du clavier, en montrant les coûts accrus en temps 
    réel. On peut aussi visualiser des flèches indiquant l’action optimale 
    d’après une politique stationnaire déterministe et utiliser une politique 
    déterministe ou mixte pour le guidage automatique du robot en tapant la 
    touche ‘espace’. 
    
    Parameters
    ----------
    grille : Grille
        La grille à visualiser. 
    tab_coul : list(string)
        List avec les codes hexadécimaux des couleurs utilisés dans la 
        visualisation de la grille. Doit avoir au moins la même quantité que 
        des couleurs dans la grille.
        
    Attributes
    ----------
    grille : Grille
        La grille à visualiser. 
    tab_coul : list(string)
        List avec les codes hexadécimaux des couleurs utilisés dans la 
        visualisation de la grille. Doit avoir au moins la même quantité que 
        des couleurs dans la grille.
    case_px : int
        La taille en pixels d’une case de la grille. Le défaut est 40.
    strategy : numpy.ndarray
        Tableau représentant une stratégie. Chaque case contient soit un nombre
        entre 0 et 3 indiquant à quelle case voisine le robot doit aller ou une
        distribution de probabilités pour les cases voisines. 
    """
    
    def __init__(self, grille, tab_coul):   
        assert (np.unique(grille.tab)).size - 1 <= len(tab_coul)
        self.grille = grille
        self.tab_coul = tab_coul
        
        
    def view(self, case_px = 40, mode = "couleur", strategy = None):
        """
        Créé une visualisation de la grille dans une fenêtre à l’aide du module
        Tkinter. 

        Parameters
        ----------
        case_px : int
            La taille en pixels d’une case de la grille. Le défaut est 40.
        mode : string
            DESCRIPTION. The default is "couleur".
        strategy : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.

        """
        self.case_px = case_px
        self.strategy = strategy
        
        # On crée la fenêtre de visualisation
        largeur = (self.grille.tab.shape[1] * self.case_px) + 41
        hauteur = (self.grille.tab.shape[0] * self.case_px) + 41
        window = tk.Tk()
        window.title("MDP")
        self._canevas = tk.Canvas(window, width = largeur, height = hauteur, bg = "#FFFFFF")
        self._canevas.focus_set()
        self._canevas.bind('<Key>', self._clavier)
        self._canevas.pack(padx = 5, pady = 5)
        w1 = tk.Label(window, text = "Costs: ", fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
        w1.pack(side = tk.LEFT, padx = 5, pady = 5) 
        
        # On garde ici le(s) coût(s) 
        self._costs = []
        # On garde ici les texts pour montrer le(s) coût(s)
        self._costs_labels = []
        
        # Coordonées du haut à gauche de la case de départ
        self._x0 = 20
        self._y0 = 20
     
        # On dessine la grille
        self.dessin_grid(largeur, hauteur)
        
        # Si on a une stratégie passé en argument et si c'est une stratégie déterministe alors on dessine des flèches indiquant où aller
        if strategy is not None and strategy.ndim == 2:
            # Code ASCII des flèches
            self._direct = ["\u2191", "\u2192", "\u2193", "\u2190"]
            self.dessin_fleche() 
        
        # Correspond à la grille présenté dans la partie 2 et 3 du projet
        if mode == "couleur":
            # Text où on montre la valeur totale des coûts pour la grille de type "chiffre"
            self._totalcosts = None 
            self.dessin_couleur()
            self._costs.append(0)
            wg = tk.Label(window, text = self._costs[0], fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
            wg.pack(side = tk.LEFT, padx = 5, pady = 5)
            self._costs_labels.append(wg)
            
        # Correspond à la grille présenté dans la partie 4 du projet     
        elif mode == "chiffre":
            self.dessin_chiffre()
            for i in range(len(self.tab_coul)):
                self._costs.append(0)
                wg = tk.Label(window, text = self._costs[i], fg = self.tab_coul[i], font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
                wg.pack(side = tk.LEFT, padx = 5, pady = 5) 
                self._costs_labels.append(wg)
            w2 = tk.Label(window, text = "Total costs: ", fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
            w2.pack(side = tk.LEFT, padx = 5, pady = 5) 
            self._totalcosts = tk.Label(window, text = str(sum(self._costs)), fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
            self._totalcosts.pack(side = tk.LEFT, padx = 5, pady = 5) 

        # Le robot 
        self._pion = self._canevas.create_oval(self._x0, self._y0, self._x0 + self.case_px, self._y0 + self.case_px, width = 2, outline = "black", fill = "yellow")
        
        # Si on dessine les flèches de la stratégie, alors on dessine aussi une flèche specialle sur le robot pour que l'action optimale reste visible 
        if strategy is not None and strategy.ndim == 2: 
            self._canevas.tag_raise(self.fleche_pion)
        
        # Boutons pour fermer la fenêtre et pour reinicialiser le parcours du robot
        tk.Button(window, text = "Quit", command = window.destroy).pack(side = tk.RIGHT, padx = 5, pady = 5)
        tk.Button(window, text = "Restart", command = self._reinitialize).pack(side = tk.RIGHT, padx = 5, pady = 5)

        # On montre la grille
        self._canevas.focus_set()
        window.mainloop()

                
    def _reinitialize(self):
        """
        Réinitialise la visualisation de la grille. 
        """
        self._x0 = 20
        self._y0 = 20
        self._canevas.coords(self._pion, self._x0, self._y0, self._x0 + self.case_px, self._y0 + self.case_px)
        for i in range(len(self._costs_labels)):
            self._costs[i] = 0
            self._costs_labels[i].config(text = str(self._costs[i]))
        if self._totalcosts is not None:
            self._totalcosts.config(text = str(sum(self._costs)))
            
    def _clavier(self, event):
        """
        Controle du robot par les flèches du clavier et action automatique 
        d'après une stratégie avec la touche espace. 
        """
        # Traduction des touches vers les chiffres
        dict_dir = {"Up": 0, "Right": 1, "Down": 2, "Left": 3}
        touche = event.keysym
        # Si une des flèches, on la passe à la fonction move directement
        if touche in dict_dir:
            self.move(dict_dir[touche])
        # Sinon et si on a une stratégie, on tire une flèche soit de façon déterministe, soit d'après la loi de probabilité de la case courante 
        elif touche == "space" and self.strategy is not None:
            j = round((self._x0 - 20) / self.case_px)
            i = round((self._y0 - 20) / self.case_px)
            strat = self.strategy[i,j]
            if self.strategy.ndim != 2:
                strat = np.random.choice(4, p = strat)  
            self.move(strat)
        
    def move(self, action):
        j = round((self._x0 - 20) / self.case_px)
        i = round((self._y0 - 20) / self.case_px)
    
        cases, p = zip(*self.grille.proba_trans(i, j, action).items())
        place = random.choices(cases, p)[0]

        if place == (i, j):
            return
        self._x0 = 20 + place[1] * self.case_px
        self._y0 = 20 + place[0] * self.case_px
        
        self._canevas.coords(self._pion, self._x0, self._y0, self._x0 + self.case_px, self._y0 + self.case_px)

        if self.strategy is not None and self.strategy.ndim == 2:
            self._canevas.itemconfig(self.fleche_pion, text = self._direct[self.strategy[place]])
            self._canevas.coords(self.fleche_pion, self._x0 + self.case_px // 2, self._y0 + self.case_px // 2) 
        
        if self._totalcosts is not None:
            indice = self.grille.tab[i, j]
            self._costs[indice] += self.grille.case_cout(i, j, "somme_chiffre")
            self._costs_labels[indice].config(text = str(self._costs[indice]))
            self._totalcosts.config(text = str(sum(self._costs)))
        else:
            indice = 0
            self._costs[indice] += self.grille.case_cout(i, j, "couleur")
            self._costs_labels[indice].config(text = str(self._costs[indice]))
 
    def dessin_fleche(self):
        for i in range(self.grille.tab.shape[0]):
            for j in range(self.grille.tab.shape[1]):
                x0 = 20 + self.case_px * j 
                y0 = 20 + self.case_px * i                
                if self.grille.tab[i,j] >= 0:
                    xc = x0 + self.case_px // 2
                    yc = y0 + self.case_px // 2
                    
                    self._canevas.create_text(xc, yc, anchor = "center", text = self._direct[self.strategy[i,j]], fill = "#C8C8C8", font = "Verdana " + str(int(-0.9 * self.case_px)) + " bold")                    

        self.fleche_pion = self._canevas.create_text(20 + self.case_px // 2, 20 + self.case_px // 2, anchor = "center", text = self._direct[self.strategy[0,0]], fill = "#C8C8C8", font = "Verdana " + str(int(-0.9 * self.case_px)) + " bold")                    
     
    def dessin_grid(self, largeur, hauteur):
        for i in range(self.grille.tab.shape[0] + 1):
            ni = self.case_px * i
            self._canevas.create_line(20, ni + 20, largeur - 20, ni + 20)
        for j in range(self.grille.tab.shape[1] + 1):
            nj = self.case_px * j
            self._canevas.create_line(nj + 20, 20, nj + 20, hauteur - 20)
    
    def dessin_couleur(self):
        circle = max(self.case_px // 6, 2)
        
        for i in range(self.grille.tab.shape[0]):
            for j in range(self.grille.tab.shape[1]):
                x0 = 20 + self.case_px * j 
                y0 = 20 + self.case_px * i                
                if self.grille.tab[i,j] >= 0:
                    c = self.tab_coul[self.grille.tab[i,j]]
                    xc = x0 + self.case_px // 2
                    yc = y0 + self.case_px // 2
                    self._canevas.create_oval(xc - circle , yc - circle, xc + circle, yc + circle, width = 1, outline = c, fill = c)
                else:
                    self._canevas.create_rectangle(x0, y0, x0 + self.case_px, y0 + self.case_px, fill = "#5E5E64")
        
    def dessin_chiffre(self):

        for i in range(self.grille.tab.shape[0]):
            for j in range(self.grille.tab.shape[1]):
                x0 = 20 + self.case_px * j 
                y0 = 20 + self.case_px * i                
                if self.grille.tab[i,j] >= 0:
                    c = self.tab_coul[self.grille.tab[i,j]]
                    xc = x0 + self.case_px // 2
                    yc = y0 + self.case_px // 2
                    
                    self._canevas.create_text(xc, yc, anchor = "center", text = str(self.grille.chiffre[i, j]),fill = c, font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
                else:
                    self._canevas.create_rectangle(x0, y0, x0 + self.case_px, y0 + self.case_px, fill = "#5E5E64")       

def pol_valeur(grille, gamma, M, eps = 1e-5, mode = "couleur"):
    vs = np.zeros(grille.tab.shape)
    vs[-1, -1] = M / (1 - gamma)
    erreur = 1 + eps
    cpt = 0
    while erreur > eps:
        erreur = 0
        for i in range(vs.shape[0]):
            for j in range(vs.shape[1]):
                if grille.tab[i, j] >= 0 and (i, j) != (vs.shape[0] - 1, vs.shape[1] - 1):
                    qat = - np.inf
                    cout = grille.case_cout(i, j, mode)
                    for a in range(4):
                        cases_p = grille.proba_trans(i, j, a)
                        q = sum([p * vs[c] for c, p in cases_p.items()])
                        qat = max(qat, q)
                    new_vs = - cout + gamma * qat
                    erreur = max(erreur, abs(vs[i, j] - new_vs))
                    vs[i, j] = new_vs
        cpt += 1
                    
    pol = np.zeros(grille.tab.shape, dtype = int)
    pol[-1, -1] = 1
    for i in range(vs.shape[0]):
        for j in range(vs.shape[1]):
            if grille.tab[i, j] >= 0 and (i, j) != (vs.shape[0] - 1, vs.shape[1] - 1):
                qat = - np.inf
                for a in range(4):
                    cases_p = grille.proba_trans(i, j, a)
                    q = sum([p * vs[c] for c, p in cases_p.items()])
                    if q > qat:
                        qat = q
                        pol[i, j] = a
    return pol, cpt


def pol_pl_mixte(grille, gamma, M, verbose = False, mode = "couleur"):
    # On créé le pl
    pl = gp.Model("mixte")
    if not verbose:
        pl.setParam("OutputFlag", 0)
    lig, col = grille.tab.shape
    
    # On créé les variables et coefficients de la fonction objectif
    var, reward = gp.multidict({(i, j, a): - grille.case_cout(i, j, mode)  
                                for i in range(lig) 
                                for j in range(col) 
                                for a in range(4) 
                                if grille.tab[i, j] >= 0})
    
    # On reajuste le coefficient de la case but 
    for a in range(4):
        reward[(lig - 1, col - 1, a)] = M
        
    # On ajoute les variables et la fonction objectif
    xsa = pl.addVars(var, name = "x")
    pl.setObjective(xsa.prod(reward), gp.GRB.MAXIMIZE)
    
    # On ajoute les contraintes
    pl.addConstrs((xsa.sum(i, j, "*") - gamma * 
                   xsa.prod(grille.proba_trans_arr(i, j)) == 4 / len(var) 
                  for i in range(lig) 
                  for j in range(col)  
                  if grille.tab[i, j] >= 0), "contr")
    # L'optimisation
    pl.optimize()
    # On créé les probabilités
    strat = None
    # On teste si on a une vrai solution
    if pl.status == gp.GRB.OPTIMAL:
        # Recuperation des solutions
        strat = np.ones((*grille.tab.shape, 4))
        solution = pl.getAttr("x", xsa)
        for key, val in solution.items():
            strat[key] = val
        # Normalisation pour trouver les probabilités
        strat = strat / strat.sum(2).reshape((lig, col, 1))  
    return strat

def pol_pl_pure(grille, gamma, M, verbose = False, mode = "couleur"):
    # On créé le pl
    pl = gp.Model("mixte")
    if not verbose:
        pl.setParam("OutputFlag", 0)
    lig, col = grille.tab.shape
    
    # On créé les variables et coefficients de la fonction objectif
    var, reward = gp.multidict({(i, j, a): - grille.case_cout(i, j, mode)  
                                for i in range(lig) 
                                for j in range(col) 
                                for a in range(4) 
                                if grille.tab[i, j] >= 0})
    
    # On reajuste le coefficient de la case but 
    for a in range(4):
        reward[(lig - 1, col - 1, a)] = M
        
    # On ajoute les variables et la fonction objectif
    xsa = pl.addVars(var, name = "x")
    dsa = pl.addVars(var, name = "d", vtype = gp.GRB.BINARY)
    
    pl.setObjective(xsa.prod(reward), gp.GRB.MAXIMIZE)
    
    # On ajoute les contraintes
    pl.addConstrs((xsa.sum(i, j, "*") - gamma * 
                   xsa.prod(grille.proba_trans_arr(i, j)) == 4 / len(var) 
                  for i in range(lig) 
                  for j in range(col)  
                  if grille.tab[i, j] >= 0), "contr_x")
    pl.addConstrs((dsa.sum(i, j, "*") <= 1 
                  for i in range(lig) 
                  for j in range(col)  
                  if grille.tab[i, j] >= 0), "contr_d")
    pl.addConstrs(((1 - gamma) * xsa[i, j, a] <= dsa[i, j, a] 
                  for i, j, a in var), "contr_xd")   
    
    # L'optimisation
    pl.optimize()
    # On créé les probabilités
    strat = None
    # On teste si on a une vrai solution
    if pl.status == gp.GRB.OPTIMAL:
        # Recuperation des solutions
        strat = np.zeros(grille.tab.shape, dtype = int)
        solution = pl.getAttr("x", dsa)
        for (i, j, a), val in solution.items():
            if val == 1:
                strat[i, j] = a
    return strat


def pol_pl_mixte_mo(grille, gamma, M, verbose = False):
    # On créé le pl
    pl = gp.Model("mixte")
    if not verbose:
        pl.setParam("OutputFlag", 0)
    lig, col = grille.tab.shape
    
    # On créé les variables et coefficients de la fonction objectif
    var, reward = gp.multidict({(i, j, a): - grille.case_cout(i, j, "somme_chiffre")  
                                for i in range(lig) 
                                for j in range(col) 
                                for a in range(4) 
                                if grille.tab[i, j] >= 0})
    
    # On reajuste le coefficient de la case but 
    for a in range(4):
        reward[(lig - 1, col - 1, a)] = M
        
    # On ajoute les variables et la fonction objectif
    xsa = pl.addVars(var, name = "x")
    z = pl.addVar(lb = -float("inf"), name = "z")
    
    pl.setObjective(z, gp.GRB.MAXIMIZE)
    
    # On ajoute les contraintes liées aux xsa
    pl.addConstrs((xsa.sum(i, j, "*") - gamma * 
                   xsa.prod(grille.proba_trans_arr(i, j)) == 4 / len(var) 
                  for i in range(lig) 
                  for j in range(col)  
                  if grille.tab[i, j] >= 0), "contr")
    
    # On ajoute les contraintes lieés à z
    for c in range(len(grille.tab_cost)):
        reward_c = dict(filter(lambda item: grille.tab[item[0][0], item[0][1]] == c, reward.items()))
        for a in range(4):
            reward_c[(lig - 1, col - 1, a)] = M
        pl.addConstr(z <= xsa.prod(reward_c), "contr_color_" + str(c))
    
    # L'optimisation
    pl.optimize()
    # On créé les probabilités
    strat = None
    # On teste si on a une vrai solution
    if pl.status == gp.GRB.OPTIMAL:
        # Recuperation des solutions
        strat = np.ones((*grille.tab.shape, 4))
        solution = pl.getAttr("x", xsa)
        for key, val in solution.items():
            strat[key] = val
        # Normalisation pour trouver les probabilités
        strat = strat / strat.sum(2).reshape((lig, col, 1))  
    return strat


def tester_temps(fonction, list_grille, repeat = 10, **kwargs):
    temps = time.process_time()
    for grille in list_grille:
        for _ in range(repeat):
            fonction(grille, **kwargs)
    temps = time.process_time() - temps 
    return temps / (len(list_grille) * repeat)
    
        
if __name__ == "__main__":
    
    red = "#F70B42"
    green = "#1AD22C"
    blue = "#0B79F7"
    gray = "#E8E8EB"
    orange = "#FFAA11"
    darkgray = "#5E5E64"
    white = "#FFFFFF"
    
    nb_color = 4
    color = [green, blue, red, darkgray]
    cost = [1, 2, 3, 4]
    width = 10
    height = 10
    gamma = 0.9
    M = 1000
    
    strategy_pur = np.random.choice(4, (height, width))
    strategy_mixte = np.random.uniform(size = (height, width, 4))
    strategy_mixte = strategy_mixte / strategy_mixte.sum(2).reshape((height, width, 1))
    strategy_mixte2 = np.ones((height, width, 4))/4
    
   
    g = Grille(height, width, tab_cost = cost, p = 1, proba_mur = 0.1)
    
    strategy_valeur, nb_iter =  pol_valeur(g, gamma = gamma, M = M)
    strategy_pl_mixte = pol_pl_mixte(g, gamma = gamma, M = M)
    strategy_pl_pure = pol_pl_pure(g, gamma = gamma, M = M)
    s = pol_pl_mixte_mo(g, gamma, M)
    
        
    v = Visualisation(g, color)
    #v.view(case_px = 50, mode = "couleur", strategy = strategy_valeur)
        
        