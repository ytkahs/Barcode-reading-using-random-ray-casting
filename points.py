#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 09:35:59 2024

@author: ines
"""

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap
import numpy as np
import skimage
from scipy import signal, interpolate
import cmath


def points(img, sig, sig_p, seuil, scale, sigma, affichage):
    
    # Créer une grille de coordonnées centrée autour de zéro
    X, Y = np.meshgrid(range(int(-3*sig), int(3*sig) + 1), range(int(-3*sig), int(3*sig) + 1))
    
    Gx = -X/(2*np.pi*sig**4)*np.exp(-(X**2+Y**2)/(2*sig**2))
    Gy = -Y/(2*np.pi*sig**4)*np.exp(-(X**2+Y**2)/(2*sig**2))
    
    I=plt.imread(img)
    R = I[:,:,0]
    G = I[:,:,1]
    B = I[:,:,2]
    L = (R+G+B)/3
    
    
    I_Gx=signal.convolve2d(L, Gx, mode='same', boundary='fill', fillvalue=0)
    I_Gy=signal.convolve2d(L, Gy, mode='same', boundary='fill', fillvalue=0)
    
    
    Ix_norm = I_Gx/ np.sqrt(I_Gx**2 + I_Gy**2)
    Iy_norm = I_Gy/ np.sqrt(I_Gx**2 + I_Gy**2)
    
    # I_normalisé=I_norm / I_norm.max()
    
    
    # Créer une grille de coordonnées centrée autour de zéro
    X, Y = np.meshgrid(range(int(-3*sig_p), int(3*sig_p) + 1), range(int(-3*sig), int(3*sig_p) + 1))
    
    G = np.exp(-(X**2 + Y**2) / (2 * sig_p**2))
    
    Txx = signal.convolve2d(Ix_norm**2, G, mode='same', boundary='fill', fillvalue=0)
    Txy = signal.convolve2d(Ix_norm*Iy_norm, G, mode='same', boundary='fill', fillvalue=0)
    Tyy = signal.convolve2d(Iy_norm**2, G, mode='same', boundary='fill', fillvalue=0)
    
    D = np.sqrt((Txx - Tyy)**2 + 4*Txy**2)/(Txx + Tyy)
    D_inv = 1-D
    
    D_M = (D_inv >= seuil)
    
    D_Label = skimage.measure.label(1-D_M)
    
    #Detection du plus gros blob
    regions=skimage.measure.regionprops(D_Label)
    blob = None
    max_area = 0
    
    
    for region in regions:
        if region.area > max_area:
            max_area = region.area
            blob = region
    
    D_fin = np.zeros_like(D_Label)
    if blob:
        D_fin[D_Label == blob.label] = 1
        
        coordonnees = blob.coords
        x = coordonnees[:,0]
        y = coordonnees[:,1]
    
        centre_x = x.mean()
        centre_y = y.mean()
        
        cov_centre_x = x - centre_x
        cov_centre_y = y - centre_y
        
        # Covariance
        n = len(x)
        var_x = np.sum(cov_centre_x**2)/n
        var_y = np.sum (cov_centre_y**2)/n
        cov_xy = np.sum(cov_centre_x*cov_centre_y)/n
        
        Cov_matrice = np.array([
            [var_x, cov_xy],
            [cov_xy, var_y]
        ])
    
    if(affichage == 1):
        print("Centre du blob : (", centre_x, ",", centre_y, ")")
        print("Matrice de covariance :\n", Cov_matrice)
        
     
    # Matrice de covariance
    a, b, c = Cov_matrice[0, 0], Cov_matrice[0, 1], Cov_matrice[1, 1]
    
    trace = a + c
    det = a*c - b**2
    lambda1 = (trace + np.sqrt(trace**2 - 4*det)) / 2
    lambda2 = (trace - np.sqrt(trace**2 - 4*det)) / 2
    
    vec_ppre1 = np.array([b, lambda1 - a])  
    vec_ppre2 = np.array([b, lambda2 - a]) 
    
    # Normalisation 
    vec_ppre1 = vec_ppre1 / np.linalg.norm(vec_ppre1)
    vec_ppre2 = vec_ppre2 / np.linalg.norm(vec_ppre2)
    
    
    if (affichage == 1):  
        print("Valeurs propres :", lambda1, lambda2)
        print("Vecteur propre 1 :", vec_ppre1)
        print("Vecteur propre 2 :", vec_ppre2)

        #Affichage
        plt.figure(1)
        plt.imshow(I, cmap='gray')
        plt.title('I')
        plt.figure(2)
        plt.imshow(L, cmap='gray')
        plt.title('L')
        plt.figure(3)
        plt.imshow(Ix_norm, cmap='gray')
        plt.title('I x norm')
        plt.figure(4)
        plt.imshow(Iy_norm, cmap='gray')
        plt.title('I y norm')
        plt.figure(5)
        plt.imshow(D, cmap='gray')
        plt.title('D')
        plt.figure(6)
        plt.imshow(D_inv, cmap='gray')
        plt.title('D inv')
        plt.figure(7)
        plt.imshow(D_M, cmap='gray')
        plt.title('D seuil')
        plt.figure(8)
        plt.imshow(D_Label)
        plt.title('D label')
        plt.figure(9)
        plt.imshow(D_fin)
        plt.title('D fin')

    
    if lambda1 > lambda2:
        direction = lambda1
        vec_principal = vec_ppre1
        length = np.sqrt(lambda1)*scale
    else:
        direction = lambda2
        vec_principal = vec_ppre2
        length = np.sqrt(lambda2)*scale
        
    # Génération de 10 points aléatoires
    num_points = 10
    
    points_droite = []
    points_gauche = []
    for _ in range(num_points//2):
        # Bruit gaussien
        noise_x = np.random.normal(0, sigma)
        noise_y = np.random.normal(0, sigma)
        
        # Point dans la direction principale
        point1 = [
            centre_x + vec_principal[0]*length + noise_x,
            centre_y + vec_principal[1]*length + noise_y
        ]

        # Point dans la direction opposée
        point2 = [
            centre_x - vec_principal[0]*length + noise_x,
            centre_y - vec_principal[1]*length + noise_y
        ]
        
        points_droite.append(point1)
        points_gauche.append(point2)
    
    points_gauche = np.array(points_gauche)
    points_droite = np.array(points_droite)

    if (affichage == 1):
        plt.figure(10)
        plt.imshow(D_fin)
        plt.scatter(centre_y, centre_x, color='red', label='Centre') #Centre
        for i in range(len(points_droite)):
            plt.scatter(points_gauche[i][1], points_gauche[i][0], color='green', s=50) #Points aléatoires
            plt.scatter(points_droite[i][1], points_droite[i][0], color='green', s=50)

        # Tracer la flèche dans un sens
        plt.arrow(
            centre_y, centre_x,   # Point de départ
            vec_principal[1]*length, vec_principal[0]*length,  # Déplacement (delta_y, delta_x)
            head_width=10, head_length=10, fc='blue', ec='blue', label='Axes'
        )
        
        # Flèche dans l'autre sens
        plt.arrow(
            centre_y, centre_x,   # Point de départ
            -vec_principal[1]*length, -vec_principal[0]*length,  # Déplacement inverse
            head_width=10, head_length=10, fc='blue', ec='blue'
        )
        
        plt.legend()
        plt.title('Blob avec centre et axe principal')
        plt.show()

    return points_gauche, points_droite

""" img='img/bouteille_simple.png'
sig = 1
sig_p = 10 #test 20
seuil = 0.25

# Vecteurs et valeurs propres
scale = 2.5
sigma = 5  
affichage = 1
    
ptsg, ptsd = points(img, sig, sig_p, seuil, scale, sigma, affichage) """