#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

# Server per gestire le richieste di accensione/spegnimento ventola (Raspberry Pi 4 model B)

# Porta d'ascolto
PORT = 3500
# N. pin GPIO
PIN = 21

# Azioni che il server può eseguire
ACTIONS = {
    1: 'on',
    2: 'off',
    3: 'status'
}

#Set up iniziale GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(PIN, GPIO.OUT)


class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    """ Classe che si occupa di istanziare un server web, 
        capace di rispondere a richieste HTTP di tipo 'GET' """

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        message = self.getAction(self.path)
        self.wfile.write(bytes(message, "utf8"))
        #GPIO.cleanup()
        return

    def getAction(self, path: str) -> str:
        
        """ Ritorna il valore della chiave action nella query string
        
        Parameters
        ----------
        path : str
             Percorso richiesto dal client """        
        
        queryString = urlparse(path)[4]
        if queryString.contains('&'):
            return queryString.split('&')[0].split('=')[1]
        else:
            return queryString.split('=')[1]

    def apply(self, action: str):
        
        """ Applica l'azione predefinita per una determinata azione
        
        Parameters
        ----------
        action : str
             Azione richeista dal client """ 
        
        if action==ACTIONS[0]:
            #GPIO.output(PIN, GPIO.HIGH)
            if GPIO.input(PIN) == 1:
                return "OK"
        elif action==ACTIONS[1]:
            #GPIO.output(PIN, GPIO.LOW)
            if GPIO.input(PIN) == 0:
                return "OK"            
        elif action==ACTIONS[2]:
            return GPIO.input(PIN)
        return "ERROR"
    
def run():
    print('Avvio del server...')
    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('Server in esecuzione...')
    httpd.serve_forever()

run()

