#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from RPi import GPIO
from urllib.parse import urlparse, parse_qs
from datetime import time, datetime
import configparser

''' Server per gestire le richieste di accensione/spegnimento ventola (Raspberry Pi 4 model B) '''

# Caricamento file di configurazione

config = configparser.ConfigParser()
config.read('server.ini')

# Porta d'ascolto
PORT = int(config['general']['port'])
# N. pin GPIO
PIN = int(config['general']['pin'])

# Azioni che il server può eseguire
ACTIONS = {
    1 : 'on',
    2 : 'off',
    3 : 'status',
    4 : 'setSS',
}

# Variabili per il salvataggio dell'orario di accensione/spegnimento output
start = datetime.fromtimestamp(int(config['general']['start']))
stop = datetime.fromtimestamp(int(config['general']['stop']))

def initGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PIN, GPIO.OUT)

initGPIO()

class ServerSays():
    
    """ Classe per mostare alcuni output del server """
    
    _colori = {
        "red": "\033[91m",
        "endc": "\033[0m"
    }
    
    @staticmethod
    def _colora(text: str, color: str) -> str:
        return ServerSays._colors[color] + text + ServerSays._colors["endc"]
    
    @staticmethod
    def simpleMessage(text: str, args: str = "") -> None:
        """ Stampa una semplice comunicazione del server
        
        Parameters
        ---------- 
        text : str
            Testo da stampare
        args : str, optional
            Argomenti per format
        """
        print("\n[SERVER] : " + text.format(args))

    @staticmethod
    def error(text: str, args: str = "") -> None:
        """ Stampa un messaggio di malfunzionamento del server o di errore
        
        Parameters
        ---------- 
        text : str
            Testo da stampare
        args : str, optional
            Argomenti per format
        """
        print("\n[SERVER] : " + ServerSays._colora("[x] " + text.format(args), "red"))   
    

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    """ Classe che si occupa di istanziare un server web, 
        capace di rispondere a richieste HTTP di tipo 'GET' """

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = self.apply(self.getAction(self.path))
        self.wfile.write(bytes(message, "utf8"))
        ServerSays.simpleMessage(self.address_string + ' served, reponse: ' + message)
        return

    def parseQS(self, path: str) -> str:
        
        """ Ritorna il valore della prima chiave nella query string
        
        Parameters
        ----------
        path : str
             Percorso richiesto dal client """        
        
        queryString = urllib.parse.parse_qs(urlparse(path)[4])
        return queryString['action'], queryString['start'], queryString['stop']

    def apply(self, action: str, start: str, stop: str) -> None:
        
        """ Applica l'azione predefinita per una determinata azione
        
        Parameters
        ----------
        action : str
             Azione richiesta dal client """ 
        
        initGPIO()
        
        if action==ACTIONS[1]:
            GPIO.output(PIN, GPIO.HIGH)
            if GPIO.input(PIN) == 1:
                return "OK"
        elif action==ACTIONS[2]:
            GPIO.output(PIN, GPIO.LOW)
            if GPIO.input(PIN) == 0:
                return "OK"            
        elif action==ACTIONS[3]:
            return GPIO.input(PIN)
        elif action==ACTIONS[4]:
            pass
        ServerSays.error("The request can't be satisfied")
        return "ERROR"
    
def run():
    ServerSays.simpleMessage('Start server on port ' + str(PORT) + '...')
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    ServerSays.simpleMessage('Server is running. Please press CTRL+C to stop safely the process.')
    httpd.serve_forever()

#Main

try:
    run()
except KeyboardInterrupt as e:
    ServerSays.error("Server stopped with an interrupt")
finally:
    GPIO.cleanup()