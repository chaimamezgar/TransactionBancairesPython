import threading
import socket
from ProjetPSR.CompteManager import findRefCompte_login, readCompte

#SERVER = socket.gethostbyname(socket.gethostname())
from ProjetPSR.FactureManager import readFacture
from ProjetPSR.TransactionManager import EffectuerTransaction

SERVER = "192.168.1.14"
PORT = 9090
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
HEADER = 64

DISCONNECT_MESSAGE = "!DISCONNECT"
ANSWER_MESSAGE = "!ANSWER"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

#Liste des connections
connections = []
#Liste des comptes en train d'effectuer des transactions
comptes_actives = []


#Connection-----------------------------------------
#Envoyer message
def send_message(conn, msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    conn.send(send_length)
    conn.send(message)
#Recevoir message
def recieve_message(conn):
    send_message(conn, ANSWER_MESSAGE)
    msg_length = conn.recv(HEADER).decode(FORMAT)
    if msg_length:
        msg_length = int(msg_length)
        msg = conn.recv(msg_length).decode(FORMAT)
    return msg


#Semaphore--------------------------------------------
def lock(conn, compte):
    if compte.refCompte in comptes_actives:
        msg = "Ce compte a une transaction en cours! Veuillez patientez!"
        send_message(conn, msg)
    while True:
        if compte.refCompte not in comptes_actives:
            break
    comptes_actives.append(compte.refCompte)
def unlock(compte):
    comptes_actives.remove(compte.refCompte)


def login(conn):
    msg = "Bienvenue chez MEZGAR & REDISSI BANKING ! \n Cher client ! Veuillez saisir votre numéro de compte :"
    send_message(conn, msg)
    refCompte = recieve_message(conn)
    refCompte.strip()
    if refCompte.lower() == "00000":  # admin
        token = {"status": True, 'data': "admin"}
    else:
        token = findRefCompte_login(refCompte)
    print(f"{refCompte} ")
    return token


def menu(conn):
    choix = '0'
    while choix not in '12345':
        msg = "Veuillez taper votre choix ( 1 - 5 ) "
        send_message(conn, msg)
        msg = "1 ----- Consulter compte ----- "
        send_message(conn, msg)
        msg = "2 ----- Debiter ----- "
        send_message(conn, msg)
        msg = "3 ----- Crediter ----- "
        send_message(conn, msg)
        msg = "4 ----- Recevoir facture ----- "
        send_message(conn, msg)
        msg = "5 XXXXX Deconnexion XXXXX"
        send_message(conn, msg)
        choix = recieve_message(conn)
        print(choix)
        if choix not in '12345':
            msg = "Choix invalide !"
            send_message(conn, msg)
    return choix

def handle_menu(conn, compte, choix):
    match choix:
        case '1':
            compte = readCompte(compte.refCompte)
            send_message(conn, str(compte))
        case '2':
            lock(conn, compte)
            msg = "Débit-------------------"
            send_message(conn, msg)
            msg = "Montant : "
            send_message(conn, msg)
            montant = int(recieve_message(conn))
            print('MOOOOOOOONTANT')
            print(montant)
            while montant < 0:
                msg = "Vous devez introduire un montant positif"
                send_message(conn, msg)
                montant = int(recieve_message(conn))

            operation = EffectuerTransaction(compte.refCompte, "retrait", montant)
            if operation == True:
                msg = f"Retrait de {montant}DT effectue avec success!"
                send_message(conn, msg)
                facture = readFacture(compte.refCompte)
                msg = "Votre Facture"
                send_message(conn, msg)
                send_message(conn, str(facture))
            else:
                msg = "ERREUR: Retrait Echoue! Vous avez depassez le plafond !"
                send_message(conn, msg)
            unlock(compte)
        case '3':
            lock(conn, compte)
            msg = "Donnez le montant a ajouter ?"
            send_message(conn, msg)
            montant = int(recieve_message(conn))
            while montant < 0:
                msg = "Vous devez introduire un montant positif"
                send_message(conn, msg)
                montant = int(recieve_message(conn))
            operation = EffectuerTransaction(compte.refCompte, "depot", montant)
            if operation == True:
                msg = f"Ajout de {montant}DT effectue avec success!"
            elif operation == False:
                msg = "ERREUR: Ajout Echoue! Reessayez !"
            send_message(conn, msg)
            unlock(compte)
        case '4':
            facture = readFacture(compte.refCompte)
            send_message(conn, str(facture))


def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    token = login(conn)
    if token['status']:
        compte = token['data']
        try:
            send_message(conn, f"Bienvenue {token['data']}")
        except:
            send_message(conn, f"Bienvenue {token['data']}")
    else:
        send_message(
            conn, "Informations Invalides! Vous avez etes deconnecte!")
        send_message(conn, DISCONNECT_MESSAGE)
        connected = False
        connections.remove(conn)
        print(f"[{addr}] was disconnected due to invalid info!")
    while connected:
        #if compte == 'admin':
         #   option = send_admin_menu(conn)
         #   if option == '5':
          #      send_message(conn, DISCONNECT_MESSAGE)
           #     connected = False
            #    connections.remove(conn)
             #   print(f"[{addr}] has disconnected!")
              #  break
            #handle_admin_option(conn, option)
        #else:
        if 'admin' != compte:
            choix = menu(conn)
            print("hedhi")
            print(choix)
            if choix == '5':
                send_message(conn, DISCONNECT_MESSAGE)
                connected = False
                connections.remove(conn)
                print(f"[{addr}] has disconnected!")
                break
            handle_menu(conn, compte, choix)
    conn.close()

def demarrer():
    server.listen()
    print(f"Bienvenu chez MEZGAR and REDISSI BANKING ")
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        connections.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


print("[STARTING] server is starting...")
demarrer()
