import os

from ProjetPSR.CompteManager import readCompte, updateCompte
from ProjetPSR.FactureManager import updateFacture

dir = os.path.join(os.getcwd(), "Data")
transactions_file = os.path.join(dir, "histo.txt")


class Transaction:
    def __init__(self, refCompte, typeTransaction, valeur, etat="", resultat=""):
        self.refCompte = refCompte
        self.typeTransaction = typeTransaction
        self.valeur = str(valeur)
        self.etat = etat
        self.resultat = resultat

    def WriteFile(self):
        f = open(transactions_file, 'w')
        data = str(self.refCompte) + ' ' + self.typeTransaction + \
               ' ' + self.valeur + ' ' + self.etat + ' ' + self.resultat
        f.write(data)
        print("Transaction historiée avec succés")
        f.close()

    def __str__(self):
        info = "ID: " + str(self.refCompte) + "\n" + "Type de Transaction: " + \
               self.typeTransaction + "\n" + "Valeur: " + self.valeur + "\n" + "Resultat: " + self.resultat
        return info

    def AfficherTransaction(self):
        print("ID: " + str(self.refCompte))
        print("Type de Transaction: " + self.typeTransaction)
        print("Valeur: " + self.valeur)
        print("Resultat: " + self.resultat)


def readTransactionByRef(ref):
    f = open(transactions_file, 'rb')
    transactions = []
    while True:
        ligne = f.readline()
        if (ligne == b''):
            break
        data = ligne.split()
        transaction = Transaction(data[0], data[1], data[2], str(data[3]), str(data[4]))
        if (int(transaction.refCompte) == ref):
            transactions.append(transaction)
    f.close()
    if (len(transactions) == 0):
        raise Exception('Le compte naucun transaction')
    return transactions


def readTransactions():
    f = open(transactions_file, 'rb')
    transactions = []
    for ligne in f.readlines():
        data = ligne.split()
        print(data)
        transaction = Transaction(data[0], data[1], data[2], str(data[3]), str(data[4]))
        transactions.append(transaction)
    f.close()
    return transactions


def EffectuerTransaction(refCompte, typeTransaction, montant):
    transaction = Transaction(refCompte, typeTransaction, montant)
    compte = readCompte(refCompte)
    test = False
    if typeTransaction == "retrait" and ((compte.etat == "positif" and int(compte.plafond) + int(compte.valeur) < int(montant)) or (compte.etat == "negatif" and int(compte.plafond) - int(compte.valeur) < int(montant))):
            transaction.resultat = "echec"
            transaction.etat = compte.etat
            transaction.WriteFile()
    else:
        test = True
        oldEtat = compte.etat
        updateCompte(refCompte, typeTransaction, montant)
        transaction.resultat = "succees"
        compte = updateCompte(refCompte, typeTransaction, montant)
        transaction.etat = compte.etat
        transaction.WriteFile()
        if compte.etat == "negatif" and typeTransaction == "retrait":
            if compte.etat != oldEtat:
                updateFacture(refCompte, int(compte.valeur))
            else:
                updateFacture(refCompte, montant)
    return test

