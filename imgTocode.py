from decode_sequence import decode_final, check_gardes, extraction
from lecture import scan
from points import points
import sys

# Prend en entrée un code barre "propre", pas de cadre de coleur autour ou quoi
# Renvoie la sequence de chiffres correspondante
def img2result(fichier, seuil=1000):
    """
    Décrypte l'image d'un code barre pour en extraire la séquence de chiffres correspondante

    Arguments:
        fichier: Chemin vers l'image d'un code barre "propre", pas de cadre de couleur autour.
        seuil (int) __optionnel__: Le nombre de tentatives de lecture de l'image maximale que le programme 
            va tenter au bout duquel il renverra une erreur

    Returns:
        la sequence de chiffres correspondante

    Assemblage du travail de Raphaël et Shakty
    """
    i = 1

    # Ines and Clara's part
    sig = 1
    sig_p = 10 #test 20
    seuil = 0.25
    scale = 2.5
    sigma = 5  
        
    pts_g, pts_d = points(fichier, sig, sig_p, seuil, scale, sigma, 0)
    for g in pts_g :
        for d in pts_d:
            i += 1
            sequence = scan(fichier, g, d, 0)
            _, liste_gardes = extraction(sequence)
            if check_gardes(liste_gardes):
                print(sequence)
                return decode_final(sequence)
    
    print(f"Erreur : 'Aucun Code Barre valide trouvé'", file=sys.stderr)
    return None
            

if __name__ == "__main__":
    for i in range(19):
        fichier = f'database/ean13_{i}.png'
        print(fichier)
        print(img2result(fichier))