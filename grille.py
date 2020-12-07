# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 21:01:59 2020

@author: arian
"""

import numpy as np
import tkinter as tk

class Grille():
    
    def __init__(self, nb_lig, nb_col, couleurs = 4, proba_coul = None, proba_mur = 0):
        """
        nb_lig : nombre de lignes de la grille
        nb_col : nombre de colonnes de la grille
        couleurs : quantité de couleurs possibles
        proba_coul : probabilité de chaque couleur (taille égale à la quantité de couleurs) si None, probabilité uniforme
        proba_mur : probabilité d'avoir des murs
        """
        assert (proba_coul is None) or (len(proba_coul) == couleurs), "Tableau des probabilités des couleurs avec la mauvaise taille"   
        proba_tab = np.empty(couleurs + 1)
        
        proba_tab[0] = proba_mur
        proba_tab[1:] = proba_coul or (np.ones(couleurs) / couleurs)
        proba_tab[1:] *= (1 - proba_mur)  
        
        self.tab = np.random.choice(couleurs + 1, (nb_lig, nb_col), p = proba_tab) - 1
        self.chiffre = None
        
    def gen_chiffre(self, proba_nb = None):
        self.chiffre = np.random.choice(9, self.tab.shape, p = proba_nb) + 1
         
class Visualisation():
    
    def __init__(self, grille, tab_coul, case_px = 40, mode = "couleur"):   
        self.grille = grille
        self.tab_coul = tab_coul
        self.case_px = case_px
        self.largeur = (grille.tab.shape[1] * case_px) + 41
        self.hauteur = (grille.tab.shape[0] * case_px) + 41
        
        window = tk.Tk()
        window.title("MDP")
        
        self.Canevas = tk.Canvas(window, width = self.largeur, height = self.hauteur, bg = "#FFFFFF")
        self.dessin_grid()
        if mode == "couleur":
            self.dessin_couleur()

        elif mode == "chiffre":
            self.dessin_chiffre()
        
        
        self.Canevas.pack(padx = 5, pady = 5)
        window.mainloop()
        
        
    def dessin_grid(self):
        for i in range(self.grille.tab.shape[0] + 1):
            ni = self.case_px * i
            self.Canevas.create_line(20, ni + 20, self.largeur - 20, ni + 20)
        for j in range(self.grille.tab.shape[1] + 1):
            nj = self.case_px * j
            self.Canevas.create_line(nj + 20, 20, nj + 20, self.hauteur - 20)
    
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
                    self.Canevas.create_oval(xc - circle , yc - circle, xc + circle, yc + circle, width = 1, outline = c, fill = c)
                else:
                    self.Canevas.create_rectangle(x0, y0, x0 + self.case_px, y0 + self.case_px, fill = "#5E5E64")
        
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
                    
                    self.Canevas.create_text(xc, yc, anchor = "center", text = str(self.grille.chiffre[i,j]),fill = c, font = "Verdana " + str(int(-0.75 * self.case_px)) + " bold")
                else:
                    self.Canevas.create_rectangle(x0, y0, x0 + self.case_px, y0 + self.case_px, fill = "#5E5E64")
        
        
if __name__ == "__main__":
    
    red = "#F70B42"
    green = "#1AD22C"
    blue = "#0B79F7"
    gray = "#E8E8EB"
    orange = "#FFAA11"
    darkgray = "#5E5E64"
    white = "#FFFFFF"
    
    color=[green, blue, red, orange]
    
    g = Grille(8, 10, proba_mur = 0.2)
    g.gen_chiffre()
    Visualisation(g, color, 60, mode = "chiffre")
        
        