import numpy as np
from skimage import io
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from skimage.filters import threshold_otsu

# Étape 1 : Échantillonnage de la première signature
def echantillonner_signature(image, point1, point2, num_points):
    height, width = image.shape
    x_vals = np.linspace(point1[0], point2[0], num_points)
    y_vals = np.linspace(point1[1], point2[1], num_points)

    if 1 == 0:

        # Affichage
        plt.figure()

        plt.subplot(1, 2, 1)
        plt.title('Image originale')
        plt.imshow(image, cmap='gray')
        plt.axis('off')

        ax = plt.subplot(1, 2, 2)
        plt.title('Image avec point de lecture')
        plt.imshow(image, cmap='gray')
        for i in range(len(x_vals)):
            ax.plot(x_vals[i], y_vals[i], 'ro')

        plt.axis('off')

        plt.show()

    # Interpolation bilinéaire
    grid_x = np.arange(width)
    grid_y = np.arange(height)
    interpolateur = RegularGridInterpolator((grid_y, grid_x), image, method='linear', bounds_error=False, fill_value=0)
    points = np.array([y_vals, x_vals]).T
    return interpolateur(points), y_vals, x_vals

# Étape 2 : Estimation du seuil d'Otsu
def calculer_seuil_otsu(signature):
    return threshold_otsu(signature)

# Étape 3 : Détection des limites gauche et droite
def detecter_limites(signature, seuil):
    binaire = signature < seuil
    gauche = np.argmax(binaire)  # Premier indice à 1
    droite = len(binaire) - 1 - np.argmax(binaire[::-1])  # Dernier indice à 1
    return gauche, droite

# Étape 3.5 : Détection des limites du cadrage blanc
def detecter_bord_blanc(signature, seuil):
    binaire = signature < seuil
    gauche = np.argmin(binaire)  # Premier indice à 0
    droite = len(binaire) - 1 - np.argmin(binaire[::-1])  # Dernier indice à 0
    return gauche, droite

# Étape 4 : Calcul des points limites du rayon utile
def calculer_points_utiles(point1, point2, gauche, droite, num_points):
    x_vals = np.linspace(point1[0], point2[0], num_points)
    y_vals = np.linspace(point1[1], point2[1], num_points)
    return (x_vals[gauche], y_vals[gauche]), (x_vals[droite], y_vals[droite])

# Étape 5 : Extraction de la seconde signature
def extraire_signature_utile(image, point1, point2, longueur):
    return echantillonner_signature(image, point1, point2, longueur)


def transcription(sequence):
    answer = ""
    for i in sequence:
        if(i == True):
            answer += "B"
        else:
            answer += "N"
    return answer

# Main
def scan(fichier, point_1, point_2, affiche):
    # Charger l'image
    image = io.imread(fichier, as_gray=True)
    
    # Extraction des points
    point1 = (point_1[1], point_1[0])
    point2 = (point_2[1], point_2[0])
    
    # Étape 1 : Première signature
    num_points = 500  # Modifiable
    signature, y_vals, x_vals = echantillonner_signature(image, point1, point2, num_points)
    
    # Étape 2 : Calcul du seuil d'Otsu
    seuil = calculer_seuil_otsu(signature)
    
    # Étape 3 : Détection des limites
    gauche, droite = detecter_limites(signature, seuil)
    
    # Étape 3.5 :  Vérifictaion du cadrage
    gauche_b, droite_b = detecter_bord_blanc(signature, seuil)

    # Si il y a des contours autour du cadre blanc contenu le code barre alors on décale nos points permettant le tirage d'un rayon aléatoire
    if(gauche_b > gauche) | (droite_b < droite):
        height, width = image.shape
        point1 = (x_vals[gauche_b], y_vals[gauche_b])
        point2 = (x_vals[droite_b], y_vals[droite_b])

        signature, _, _ = echantillonner_signature(image, point1, point2, num_points)
        seuil = calculer_seuil_otsu(signature)
        gauche, droite = detecter_limites(signature, seuil)

    # Étape 4 : Points limites du rayon utile
    point_util_1, point_util_2 = calculer_points_utiles(point1, point2, gauche, droite, num_points)
    
    # Étape 5 : Seconde signature
    longueur_finale = 95  # Multiple de 95
    signature_utile, _, _ = extraire_signature_utile(image, point_util_1, point_util_2, longueur_finale)
    
    # Étape 6 : Binarisation de la seconde signature
    signature_binaire = signature_utile > seuil

    if affiche == 1:
    
        # Résultats
        print("Longueur de la premiere signature:", len(signature))
        print("Seuil d'Otsu :", seuil)
        print("Limites gauche-droite :", gauche, droite)
        print("Signature binaire :", signature_binaire)
        print(len(signature_binaire))
    
        # Affichage
        plt.figure()
        plt.plot(signature, label="Première signature")
        plt.axvline(gauche, color="green", linestyle="--", label="Gauche")
        plt.axvline(droite, color="red", linestyle="--", label="Droite")
        plt.legend()
        plt.show()
        
        plt.figure()
        plt.plot(signature_utile, label="Seconde signature")
        plt.plot(signature_binaire, label="Signature binaire")
        plt.legend()
        plt.show()


    return transcription(signature_binaire)
