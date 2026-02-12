import barcode
import random
import os
from barcode.writer import ImageWriter


# Paramètres
ean13_class = barcode.get_barcode_class('ean13')    # Type d'encodage du code_barre
N = 20  #Nombre de codes à générer
output_folder = "database"  # Dossier de destination des images


"""
Script permettant la création d'images de codes barres

Vous pouvez soit juste lancer le script en modifiant les paramètres ci-dessus ou faire appel
aux fonctions de manière individuelles

Travail de Raphaël
"""






# Crée une image d'un code barre correspondant à la séquence donnée et lui donne le nom ean13_id
def build_CodeBarre(sequence, id):
    """
    Crée une image d'un code barre correspondant à la séquence donnée et lui donne le nom ean13_id

    Inputs:
        sequence: chaine de 12 chiffres à encoder en code barre
        id: le numero du code barre qui sera mis dans le nom du fichier

    Returns:
        none

    Travail de Raphaël
    """

    # Gestion du cas où la séqeunce est invalide    
    if len(sequence) != 12:
        raise ValueError(f"La séquence doit contenir exactement 12 caractères. Longueur actuelle : {len(sequence)}")


    # Vérifier que la séquence contient uniquement des chiffres
    if not sequence.isdigit():
        raise ValueError("La séquence doit contenir uniquement des chiffres (0-9).")
    

    ean13 = ean13_class(sequence, writer=ImageWriter())
    filename = os.path.join(output_folder, "ean13_" + str(id))
    ean13.save(filename)
    print(f"EAN-13 généré et sauvegardé dans : {filename}")


# Générer une séquence aléatoire de chiffres (0-9)
def generate_random_digits(length):
    return ''.join(str(random.randint(0, 9)) for _ in range(length))


# Génère N code barre de type EAN13
def main(N):
    """
    Crée N images de codes barres aléatoires

    Inputs:
        N: Nbr de codes barres à créer

    Returns:
        none

    Travail de Raphaël
    """

    for i in range(N):
        sequence = generate_random_digits(12)
        build_CodeBarre(sequence, i)



if __name__ == "__main__":
    main(N)
