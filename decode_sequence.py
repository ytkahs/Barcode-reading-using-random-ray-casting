import sys
from itertools import chain

import numpy as np

"""
---> from decode_sequence.py import decode_final
Decode Sequence décode une séquence de 95 lettres B/N correspondant à un code-barre codé en EAN13 en une séquence de 13 chiffres
INPUT: chaine de 95 caractères B/N
    ex:\"NBNBBBNNBNBBBNNBNBBBNNBNBBBNNBNBBBNNBNBBBNNBNBNBNBBBBNNBNBBBNNBNBBBNNBNBBBNNBNBBBNNBNBBBNNBNNBN\"
OUTPUT: liste de 13 chiffres 0à9
    ex:
"""


table_correspondance = [
    ["BBBNNBN", "BNBBNNN", "NNNBBNB"],
    ["BBNNBBN", "BNNBBNN", "NNBBNNB"], 
    ["BBNBBNN", "BBNNBNN", "NNBNNBB"], 
    ["BNNNNBN", "BNBBBBN", "NBBBBNB"], 
    ["BNBBBNN", "BBNNNBN", "NBNNNBB"], 
    ["BNNBBBN", "BNNNBBN", "NBBNNNB"], 
    ["BNBNNNN", "BBBBNBN", "NBNBBBB"], 
    ["BNNNBNN", "BBNBBBN", "NBBBNBB"], 
    ["BNNBNNN", "BBBNBBN", "NBBNBBB"], 
    ["BBBNBNN", "BBNBNNN", "NNNBNBB"]]


table_firstDigit = [
    "AAAAAA",
    "AABABB",
    "AABBAB",
    "AABBBA",
    "ABAABB",
    "ABBAAB",
    "ABBBAA",
    "ABABAB",
    "ABABBA",
    "ABBABA"
]

table_lettres = ["A", "B", "C"]


def conversion(chaine):
    new_chaine = ""
    for chiffre in chaine:
        if chiffre == 0:
            new_chaine += "N"
        elif chiffre == 1:
            new_chaine += "B"
        else:
            new_chaine += chiffre
    return new_chaine


def seqTObin(suite_elements):
    somme = 0
    for z in range(len(suite_elements)):
        if suite_elements[z] == "B" or suite_elements[z] == 1:
            coeff = 1
        else:
            coeff = 0
        somme += coeff * pow(2, z)
    return somme


def tableTObin(table_lettre):
    answer = np.zeros((10, 3))
    for i in range(len(table_lettre)):
        for j in range(len(table_lettre[i])):
            suite_elements = table_lettre[i][j]
            answer[i][j] = seqTObin(suite_elements)

    return answer


def seqTOnumlettre(sequence):

    for i in range(len(table_correspondance)):
        for j in range(len(table_correspondance[i])):

            if table_correspondance[i][j] == sequence:
                return i, j

    print(f"Erreur : {'La séquence ' + sequence + ' ne correspond à aucun chiffre'}", file=sys.stderr)

    return None


# Prend en entrée une chaine de 6 lettres et renvoie le chiffre qui découle des ces catégories
def deduce_firstDigit(chaine_lettres):

    if len(chaine_lettres) != 6:
        print(f"Erreur : {'Attend une chaine de 6 lettres en entrée'}", file=sys.stderr)
        

    for ii in range(len(table_firstDigit)):
        if table_firstDigit[ii] == chaine_lettres:
            return ii

    print(chaine_lettres)

    print(f"Erreur : {'Cette chaine de lettre ne correspond à aucun premier chiffre valide'}", file=sys.stderr)
    return None



def decodage(liste_sequences):

    liste_chiffres = [99]
    liste_categories = ""

    for sequence in liste_sequences:
        if(seqTOnumlettre(sequence) != None):
            chiffre, lettre = seqTOnumlettre(sequence)
            liste_chiffres.append(chiffre)
            if table_lettres[lettre] == "C":
                liste_categories += "A"
            else:
                liste_categories += table_lettres[lettre]

        liste_chiffres[0] = deduce_firstDigit(liste_categories[0:6])

    return liste_chiffres



# Prend en entrée une liste de 95 élements et renvoie 2 liste
# - Liste des 12 séquences correpspondants à des chiffres
# - Listes des 3 gardes
def extraction(liste):
    """
    Décompose une séquence de 95 N/B en ses 3 gardes et ses deux sequences correspondants à des chiffres

    Inputs:
        liste (string of N/B): Une chaine de 95 caractères N/B d'un code barre à vérifier

    Returns:
        liste_sequences (couple of list of N/B): Les 2 séquences de 12 chiffres
        liste_gardes (tuples of list of N/B): Les 2 gardes normales et la garde centrale

    Travail de Raphaël
    """

    # Gestion des erreurs
    if len(liste) != 95:
        print(f"Erreur : {'La liste en entrée doit contenir 95 valeurs de type B/N ou 1/0'}", file=sys.stderr)


    # Gestion des gardes normales au début et à la fin
    garde_gauche = liste[:3]


    liste_sequences = []
    liste_gardes = [garde_gauche]

    # Gestion des 6 premiers chiffres
    for ii in range(6):
        debut = 3+(ii*7)
        suite = liste[debut:debut+7]
        liste_sequences.append(suite)

    # gestion de la garde centrale
    debut_garde_centrale = 3 + 6*7
    len_garde_centrale = 5
    suite = liste[debut_garde_centrale: debut_garde_centrale + len_garde_centrale]
    liste_gardes.append(suite)


    # Gestion des 6 premiers chiffres
    for ii in range(6):
        debut = debut_garde_centrale + len_garde_centrale + ii*7
        suite = liste[debut:debut + 7]
        liste_sequences.append(suite)

    # Gestion de la garde droite
    garde_droite = liste[-3:]
    liste_gardes.append(garde_droite)

    return liste_sequences, liste_gardes


# Prend en entrée les 3 gardes (droite, centrale et gauche) et renvoie true si celles-ci sont valides
def check_gardes(liste_gardes, retour_erreur = False):
    """
    Vérifie les 3 gardes d'un code barre pour checker si la séquence de NB est valide

    Inputs:
        liste_gardes (list of string of N/B): Un tuple composé des 2 gardes normales au début et à la fin 
            et de la garde centrale
        retour_erreur (boolean) __optionel__ : Mettre True pour afficher les codes d'erreurs de type 
            "La garde droite n'est pas valide"

    Returns:
        (boolean): Renvoie True si les 3 gardes sont valides, False sinon

    Travail de Raphaël
    """

    if len(liste_gardes) != 3:
        print(f"Erreur : {'Veuillez mettre en entrée les 3 gardes'}", file=sys.stderr)

    garde_gauche = liste_gardes[0]
    garde_centrale = liste_gardes[1]
    garde_droite = liste_gardes[2]

    to_return = True

    garde_normale_attendue = "NBN"
    garde_centrale_attendue = "BNBNB"


    if garde_gauche != garde_normale_attendue:
        if retour_erreur == True:
            print("Input: " + garde_gauche + " | vs Attendu: " + garde_normale_attendue)
            print("Erreur: La garde GAUCHE n'est pas valide!")
        to_return = False

    if garde_droite != "NBN":
        if retour_erreur == True:
            print("Input: " + garde_droite + " | vs Attendu: " + garde_normale_attendue)
            print("Erreur: La garde DROITE n'est pas valide!")
        to_return = False

    if garde_centrale != garde_centrale_attendue:
        if retour_erreur == True:
            print("Input: " + garde_centrale + " | vs Attendu: " + garde_centrale_attendue)
            print("Erreur: La garde CENTRALE n'est pas valide")
        to_return = False

    return to_return



def liste_to_str(liste):
    chaine = ""
    for i in liste:
        chaine += str(i)
    return chaine


# La fonction qui les assemble toutes
def decode_final(chaine_to_decode):
    """
    Fonction qui décode une séquece de N/B pour en extraire le code barre correspondant

    Inputs:
        chaine_to_decode (String of 95 N/B): La sequence de N/B correspondant à un parcors du code_barre
    
    Returns:
        chaine (String of 12 digits): Le code barre décrypté correspondant

    Travail de Raphaël
    """

    sequences, gardes = extraction(chaine_to_decode)
    if check_gardes(gardes):
        liste_digit = decodage(sequences)

        chaine = ""
        chaine += str(liste_digit[0])
        chaine += " "
        chaine += liste_to_str(liste_digit[1:7])
        chaine += " "
        chaine += liste_to_str(liste_digit[7:])

        return chaine

    else:
        return None

