import os

from ProjetPSR.FactureManager import readFacture, Facture

dir = os.path.join(os.getcwd(), "Data")
comptes_file = os.path.join(dir, "comptes.txt")


class Compte:
    def __init__(self, refCompte, valeur, etat, plafond):
        self.refCompte = refCompte
        self.valeur = valeur
        self.etat = etat
        self.plafond = plafond

    def WriteFile(self):
        f = open(comptes_file, 'w')
        data = self.refCompte+ " " + self.valeur+ " " + self.etat+ " " + self.plafond
        f.write(data)
        print("Compte crée avec succés")
        f.close()

    def __str__(self):
        info = "ID: " + str(self.refCompte) + "\n" + "Valeur: " + str(self.valeur) + "\n" + "Etat: " + str(
            self.etat) + "\n" + "Plafond: " + str(self.plafond)
        return info

    def AfficherCompte(self):
        print("ID: " + str(self.refCompte))
        print("Valeur: " + str(self.valeur))
        print("Etat: " + str(self.etat))
        print("Plafond: " + str(self.plafond))


def readCompte(ref):
    f = open(comptes_file, 'rb')
    while True:
        ligne = f.readline()
        if (ligne == b''):
            break
        data = ligne.split()
        compte = Compte(data[0], data[1], data[2], data[3] )
        if (int(compte.refCompte) == int(ref)):
            return compte
    f.close()
    raise Exception("Le compte est introvable")


def readComptes():
    f = open(comptes_file, 'rb')
    comptes = []
    while True:
        ligne = f.readline()
        if (ligne == b''):
            break
        data = ligne.split()
        compte = Compte(data[0], data[1], data[2], data[3])
        comptes.append(compte)
    f.close()
    return comptes


def updateCompte(ref, type, montant):
    f = open(comptes_file, 'rb')
    comptes = []
    while True:
        ligne = f.readline()
        if (ligne == b''):
            break
        data = ligne.split()
        print(len(data))
        compte = Compte(data[0], data[1], data[2], data[3])
        if int(compte.refCompte) == int(ref):
            if type == "depot":
                print("ajout")
                if compte.etat == "positif":
                    print("positif")
                    compte.valeur = str(montant + int(compte.valeur))
                elif compte.etat == "negatif":
                    if montant > int(compte.valeur):
                        compte.valeur = str(montant - int(compte.valeur))
                        compte.etat = "positif"
                    else:
                        compte.valeur = str(int(compte.valeur) - montant)
            elif type == "retrait":
                if compte.etat == "positif" and int(compte.plafond) + int(compte.valeur) < int(montant) or compte.etat == "negatif" and int(compte.plafond) - int(compte.valeur) < int(montant):
                    raise Exception("Le solde de votre Compte est unsuffisent")
                elif compte.etat == "negatif":
                    compte.valeur = str(montant + int(compte.valeur))
                elif compte.etat == "positif":
                    if montant > int(compte.valeur):
                        compte.valeur = str(montant - int(compte.valeur))
                        compte.etat = "negatif"
                    else:
                        compte.valeur = str(int(compte.valeur) - montant)
            else:
                raise Exception("type de transaction est indefini")
        comptes.append(compte)


    f.close()
    # Clear the file
    f = open(comptes_file, 'w')
    f.close()
    print("lenArray:" + str(len(comptes)))
    for compte in comptes:
        compte.AfficherCompte()
        #compte.WriteFile()
    print("Compte modifie avec success")


def addCompte(refCompte, plafond, valeur=0, etat="positif"):
    try:
        readCompte(refCompte)
        readFacture(refCompte)
        return False
    except:
        #Compte(refCompte, valeur, etat, plafond).WriteFile()
        Facture(refCompte, 0).WriteFile()
        return True


def findRefCompte(refCompte):
    f = open(comptes_file, 'rb')
    while True:
        ligne = f.readline()
        print(ligne)
        # if(ligne == b''):
        if (ligne == ''):
            break
        data = ligne.split()
        compte = Compte(data[0], data[1], data[2], data[3])
        if (int(compte.refCompte) == int(refCompte)):
            return True
    f.close()
    return False


def findRefCompte_login(refCompte):
    f = open(comptes_file, 'rb')
    resultat = dict()
    while True:
        ligne = f.readline()
        print(ligne)
        # if(ligne == b''):
        if (ligne == ''):
            break
        data = ligne.split()
        compte = Compte(data[0], data[1], data[2], data[3])
        if (int(compte.refCompte) == int(refCompte)):
            resultat['status'] = True
            resultat['data'] = compte
            return resultat
    f.close()
    resultat['status'] = False
    return resultat
