"""
Program description:
This is a server for a draw my thing game made by Guy and Yoav.

TODO:
"""

import socket
from random import choice
from select import select
from PIL import Image
"""
class GameManager(object):
    def __init__(self, game_list):
        self.games = game_list
        
    def __listen__(self):
        changed_games = select(game_list, [], 0)[0]
"""


class Game(object):
    def __repr__(self):
        return "Game : {\nPlayers: %s\nport: %s\nRound: %s\n\n}" % (self.players, self.port, self.round) 
    
    def __init__(self, port, player_limit, max_rounds):
        self.port = port
        self.img = PIL.Image.new('RGB', (400,400), color='white')
        self.players = [] # constructed of pairs (connection, address, score)
        self.server = socket.socket()
        self.player_limit = player_limit
        self.max_rounds = max_rounds
        self.do_lobby()
        self.game_loop()
        self.server.close()
        print("[-] Game closed")
       
    def do_lobby(self):
        try:
            # Create server and bind it to port.
            self.server.bind(('', port))
        except:
            raise Exception("Could not start server...")

        self.server.listen(2) 
        self.servers = [self.server]
        self.start_game = False
        # Loop until either game starts or player limit is reached
        print("[+] Starting lobby")
        while len(self.players) <= player_limit and not self.start_game:
            read, write, err = select.select(self.servers + players, players , [])
            for serv in readable:
                if serv is server:
                    self.accept_connection(serv)
                else:
                    self.accept_input(serv)
    
    def __get_random_words__(self):
        words = []
        with open("word_list.txt", "r") as f :
            text = f.read().splitlines()
            for i in range(3):
                words.append(choice(text))
        return words
    
    def execute_round(self, round):
        self.round = round
        words = __get_random_words__()
        # TODO : Broadcast round is beginning, start timer, let drawing person pick word
        
    def game_loop():
        for round in range(1, self.max_rounds + 1):
            self.execute_round(round)
            
        
        
    def accept_connection(self, serv):
        # Get new connection:
        conn, addr = serv.accept()
        if (not self.__in_players__(addr)):
            conn.setblocking(0) # In order for the .recv() to not block
            self.players.append((conn, addr, 0))
            self.servers.append(conn)
        else:
            conn.send("Already connected from this IP...")
            conn.close()


    def accept_input(self, serv):
        data = serv.recv(1024)
        if data:
            # TODO : Add data to chat / Start game with data
        else:
            self.players.remove(serv)
            serv.close()
            print("A Player has disconnected...")
    
    def __in_players__(self, addr):
        for player in self.players:
            if (player[1][0] == addr[0]):
                return True
        return False