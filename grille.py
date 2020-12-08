# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 21:01:59 2020

@author: arian
"""

import numpy as np
import tkinter as tk

class Grille():
    
    def __init__(self, nb_lig, nb_col, couleurs = 4, tab_cost = [1, 2, 3, 4], proba_coul = None, proba_mur = 0):
        """
        nb_lig : nombre de lignes de la grille
        nb_col : nombre de colonnes de la grille
        couleurs : quantité de couleurs possibles
        tab_cost : prix de chaque couleur
        proba_coul : probabilité de chaque couleur (taille égale à la quantité de couleurs) si None, probabilité uniforme
        proba_mur : probabilité d'avoir des murs
        """
        assert (proba_coul is None) or (len(proba_coul) == couleurs), "Tableau des probabilités des couleurs avec la mauvaise taille"   
        assert (len(tab_cost) == couleurs)
        proba_tab = np.empty(couleurs + 1)
        
        proba_tab[0] = proba_mur
        proba_tab[1:] = proba_coul or (np.ones(couleurs) / couleurs)
        proba_tab[1:] *= (1 - proba_mur)  
        
        self.tab = np.random.choice(couleurs + 1, (nb_lig, nb_col), p = proba_tab) - 1
        self.tab_cost = tab_cost
        self.chiffre = None
        
    def gen_chiffre(self, proba_nb = None):
        self.chiffre = np.random.choice(9, self.tab.shape, p = proba_nb) + 1
         
class Visualisation():
    
    def __init__(self, grille):   
        self.grille = grille
        
        
    def view(self, tab_coul, p = 1, case_px = 40, mode = "couleur", strategy = None):
        
        self.tab_coul = tab_coul
        self.p = p   
        self.case_px = case_px
        self.strategy = strategy
        
        self.largeur = (self.grille.tab.shape[1] * case_px) + 41
        self.hauteur = (self.grille.tab.shape[0] * case_px) + 41
        
        self.window = tk.Tk()
        self.window.title("MDP")
        self.canevas = tk.Canvas(self.window, width = self.largeur, height = self.hauteur, bg = "#FFFFFF")
        self.canevas.focus_set()
        self.canevas.bind('<Key>', self.clavier)
        self.canevas.pack(padx = 5, pady = 5)
        
        w1 = tk.Label(self.window, text = "Costs: ", fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
        w1.pack(side = tk.LEFT, padx = 5, pady = 5) 
        self.totalcosts = None
        
        self.costs = []
        self.costs_labels = []
        self.x0 = 20
        self.y0 = 20
     
        self.dessin_grid()
        if strategy is not None and strategy.ndim == 2:
            self.direct = ["\u2191", "\u2192", "\u2193", "\u2190"]
            self.dessin_fleche() 
        
        if mode == "couleur":
            self.dessin_couleur()
            self.costs.append(0)
            wg = tk.Label(self.window, text = self.costs[0], fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
            wg.pack(side = tk.LEFT, padx = 5, pady = 5)
            self.costs_labels.append(wg)
             
        elif mode == "chiffre":
            self.dessin_chiffre()
            for i in range(len(self.tab_coul)):
                self.costs.append(0)
                wg = tk.Label(self.window, text = self.costs[i], fg = self.tab_coul[i], font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
                wg.pack(side = tk.LEFT, padx = 5, pady = 5) 
                self.costs_labels.append(wg)
            w2 = tk.Label(self.window, text = "Total costs: ", fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
            w2.pack(side = tk.LEFT, padx = 5, pady = 5) 
            self.totalcosts = tk.Label(self.window, text = str(sum(self.costs)), fg = "#5E5E64", font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
            self.totalcosts.pack(side = tk.LEFT, padx = 5, pady = 5) 

        self.pion = self.canevas.create_oval(self.x0, self.y0, self.x0 + self.case_px, self.y0 + self.case_px, width = 2, outline = "black", fill = "yellow")
        if strategy is not None and strategy.ndim == 2: 
            self.canevas.tag_raise(self.fleche_pion)
        tk.Button(self.window, text = "Quit", command = self.window.destroy).pack(side = tk.RIGHT, padx = 5, pady = 5)
        tk.Button(self.window, text = "Restart", command = self.initialize).pack(side = tk.RIGHT, padx = 5, pady = 5)

        self.canevas.focus_set()
        self.window.mainloop()

                
    def initialize(self):
        # cout et affichage
        self.x0 = 20
        self.y0 = 20
        self.canevas.coords(self.pion, self.x0, self.y0, self.x0 + self.case_px, self.y0 + self.case_px)
        
        for i in range(len(self.costs_labels)):
            self.costs[i] = 0
            self.costs_labels[i].config(text = str(self.costs[i]))
        if self.totalcosts is not None:
            self.totalcosts.config(text = str(sum(self.costs)))
            
    def clavier(self, event):
        touche = event.keysym
        if touche != "space" or self.strategy is None:
            self.move(touche)
        else:
            j = round((self.x0 - 20) / self.case_px)
            i = round((self.y0 - 20) / self.case_px)
            pos = ["Up", "Right", "Down", "Left"]  
            
            strat = self.strategy[i,j]
            if self.strategy.ndim != 2:
                strat = np.random.choice(4, p = strat)  
            self.move(pos[strat])
        
    def move(self, touche):
        j = round((self.x0 - 20) / self.case_px)
        i = round((self.y0 - 20) / self.case_px)
        place = None
        if touche == "Down" and self.grille.tab.shape[0] > i + 1 and self.grille.tab[i + 1, j] >= 0:
            case_droite = self.grille.tab.shape[1] > j + 1 and self.grille.tab[i + 1, j + 1] >= 0
            case_gauche = j - 1 >= 0 and self.grille.tab[i + 1, j - 1] >= 0
            d = np.random.choice([-1 * case_gauche, 0, 1 * case_droite], p = [(1 - self.p) / 2, self.p, (1 - self.p) / 2])
            self.y0 += self.case_px
            self.x0 += self.case_px * int(d)
            place = (i + 1, j + d)
            
        elif touche == "Up" and (i - 1) >= 0 and self.grille.tab[i - 1, j] >= 0:
            case_droite = self.grille.tab.shape[1] > j + 1 and self.grille.tab[i - 1, j + 1] >= 0
            case_gauche = j - 1 >= 0 and self.grille.tab[i - 1, j - 1] >= 0
            d = np.random.choice([-1 * case_gauche, 0, 1 * case_droite], p = [(1 - self.p) / 2, self.p, (1 - self.p) / 2])            
            self.y0 -= self.case_px
            self.x0 += self.case_px * int(d)
            place = (i - 1, j + d)
            
        elif touche == "Left" and (j - 1) >= 0 and self.grille.tab[i, j - 1] >= 0:
            case_bas = self.grille.tab.shape[0] > i + 1 and self.grille.tab[i + 1, j - 1] >= 0
            case_haut = i - 1 >= 0 and self.grille.tab[i - 1, j - 1] >= 0

            d = np.random.choice([-1 * case_haut, 0, 1 * case_bas], p = [(1 - self.p) / 2, self.p, (1 - self.p) / 2])
            self.x0 -= self.case_px
            self.y0 += self.case_px * int(d)
            place = (i + d, j - 1)
            
        elif touche == "Right" and self.grille.tab.shape[1] > j + 1 and self.grille.tab[i, j + 1] >= 0:
            case_bas = self.grille.tab.shape[0] > i + 1 and self.grille.tab[i + 1, j + 1] >= 0
            case_haut = i - 1 >= 0 and self.grille.tab[i - 1, j + 1] >= 0
            d = np.random.choice([-1 * case_haut, 0, 1 * case_bas], p = [(1 - self.p) / 2, self.p, (1 - self.p) / 2])
            self.x0 += self.case_px
            self.y0 += self.case_px * int(d)
            place = (i + d, j + 1)
            
        self.canevas.coords(self.pion, self.x0, self.y0, self.x0 + self.case_px, self.y0 + self.case_px)

        if place is not None:
            if self.strategy is not None and self.strategy.ndim == 2:
                self.canevas.itemconfig(self.fleche_pion, text = self.direct[self.strategy[place]])
                self.canevas.coords(self.fleche_pion, self.x0 + self.case_px // 2, self.y0 + self.case_px // 2) 
            if self.totalcosts is not None:
                indice = self.grille.tab[place]
                self.costs[indice] += self.grille.chiffre[place]
                self.costs_labels[indice].config(text = str(self.costs[indice]))
                self.totalcosts.config(text = str(sum(self.costs)))
            else:
                indice = 0
                self.costs[indice] += self.grille.tab_cost[self.grille.tab[place]]
                self.costs_labels[indice].config(text = str(self.costs[indice]))
 
    def dessin_fleche(self):
        for i in range(self.grille.tab.shape[0]):
            for j in range(self.grille.tab.shape[1]):
                x0 = 20 + self.case_px * j 
                y0 = 20 + self.case_px * i                
                if self.grille.tab[i,j] >= 0:
                    xc = x0 + self.case_px // 2
                    yc = y0 + self.case_px // 2
                    
                    self.canevas.create_text(xc, yc, anchor = "center", text = self.direct[self.strategy[i,j]], fill = "#C8C8C8", font = "Verdana " + str(int(-0.9 * self.case_px)) + " bold")                    

        self.fleche_pion = self.canevas.create_text(20 + self.case_px // 2, 20 + self.case_px // 2, anchor = "center", text = self.direct[self.strategy[0,0]], fill = "#C8C8C8", font = "Verdana " + str(int(-0.9 * self.case_px)) + " bold")                    
     
    def dessin_grid(self):
        for i in range(self.grille.tab.shape[0] + 1):
            ni = self.case_px * i
            self.canevas.create_line(20, ni + 20, self.largeur - 20, ni + 20)
        for j in range(self.grille.tab.shape[1] + 1):
            nj = self.case_px * j
            self.canevas.create_line(nj + 20, 20, nj + 20, self.hauteur - 20)
    
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
                    self.canevas.create_oval(xc - circle , yc - circle, xc + circle, yc + circle, width = 1, outline = c, fill = c)
                else:
                    self.canevas.create_rectangle(x0, y0, x0 + self.case_px, y0 + self.case_px, fill = "#5E5E64")
        
    def dessin_chiffre(self):

        assert self.grille.chiffre is not None, "La grille des chiffres n'a pas été initialisée"

        for i in range(self.grille.tab.shape[0]):
            for j in range(self.grille.tab.shape[1]):
                x0 = 20 + self.case_px * j 
                y0 = 20 + self.case_px * i                
                if self.grille.tab[i,j] >= 0:
                    c = self.tab_coul[self.grille.tab[i,j]]
                    xc = x0 + self.case_px // 2
                    yc = y0 + self.case_px // 2
                    
                    self.canevas.create_text(xc, yc, anchor = "center", text = str(self.grille.chiffre[i,j]),fill = c, font = "Verdana " + str(int(-0.5 * self.case_px)) + " bold")
                else:
                    self.canevas.create_rectangle(x0, y0, x0 + self.case_px, y0 + self.case_px, fill = "#5E5E64")       

        
        
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
    width = 20
    height = 10
    strategy_pur = np.random.choice(4, (height, width))
    strategy_mixte = np.random.uniform(size = (height, width, 4))
    strategy_mixte = strategy_mixte / strategy_mixte.sum(2).reshape((height, width, 1))
    strategy_mixte2 = np.ones((height, width, 4))/4
    
    g = Grille(height, width, tab_cost = cost, proba_mur = 0)
    g.gen_chiffre()
    v = Visualisation(g)
    v.view(color, p = 0.7, case_px = 50, mode = "couleur", strategy = strategy_mixte2)
        
        