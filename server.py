"""
Program description:
This is a server for a draw my thing game made by Guy and Yoav.

TODO: 
1. Think of new abilities
2. Try playing

"""
from threading import Timer
import socket, sys, signal, os, time, os.path
from PIL import Image
from random import choice
from select import select


"""
class GameManager(object):
    def __init__(self, game_list):
        self.games = game_list
        
    def __listen__(self):
        changed_games = select(game_list, [], 0)[0]
"""

MAX_ROUNDS = 10

class Ability(object):
    """
    Ability object is supposed to represent an 
    ability each player has in his ability list
    
    @cost       = Cost of ability
    @name       = Name of ability
    @cooldown   = Cooldown of ability (seconds)
    last_used   = Last time ability was used
    """
    def __init__(self, cost, name, cooldown, effect_last):
        self.cooldown   = cooldown
        self.last_used  = None
        self.name       = name
        self.cost       = cost
        self.time_last  = effect_last

    def cast(self):
        curtime = time.time()
        if (self.last_used == None):
            self.last_used = curtime
            return True
        elif (curtime - self.last_used >= cooldown):
            self.last_used = curtime
            return True
        return False
    

class Player(object):
    """
    Represents a player.

    @conn       = A player's socket connection      (socket type)
    @init_mana  = Initial mana a player begins with (int type)
    @name       = A player's name                   (string type)
    @abilities  = A player's abilities              (list of abilities class type)
    @ip         = A player's IP                     (string)
    """
    def __init__(self, conn, init_mana, name, abilities, ip):
        self.mana       = init_mana
        self.name       = name
        self.abilities  = abilities
        self.conn = conn 
        self.score      = 0
        self.ip         = ip
        self.state      = 0 # State is represented by each bit of the number
        # 0         0               0               0              0           0           0           0
        # Blind    Blind Team                       Give letter      
        # specific                   
        # person
    

    
    def __get_place__(self, ability_name):
        if ability_name == "blind_person":
            place = 1 << 8
        elif ability_name == "blind_team":
            place = 1 << 7
        elif ability_name == "draw_screen": # TODO : REPLACE ABILITY
            place = 1 << 6
        elif ability_name == "get_letter":
            place = 1 << 5
        return place 

    def remove_state(self, ability_name):
        ability_name = ability_name.lower()
        place = self.__get_place__(ability_name)
        if (self.state & place != 0):
            self.state -= place

        print("[STATE] Removed state {} from {}".format(ability_name, self.name))
    

    def add_state(self, ability_name):
        ability_name = ability_name.lower()
        place = self.__get_place__(ability_name)
        if (self.state & place == 0):
            self.state += place
        
        print("[STATE] Added state {} to {}".format(ability_name, self.name))


class Game(object):
    def __repr__(self):
        return "Game : {\nPlayers: %s\nport: %s\n\n}" % (self.players, self.port) 
    
    def __del__(self):
        print("Shutting down server...")
        erase_rounds()

    def __init__(self, port, player_limit, max_rounds):
        self.picked_word = False
        self.receiving_image = False
        self.drawer = None
        self.round_words = []
        self.port = port
        self.drawers = []
        self.players = []

        self.server = socket.socket()
        self.player_limit = player_limit
        self.max_rounds = max_rounds
        print("Game is running on ({}:{})".format("127.0.0.1", self.port))
        print("[+] Set player limit to {}".format(self.player_limit))
        print("[+] Set max rounds to {}".format(self.max_rounds))
        print("[+] Starting lobby\n [+] Waiting for players to connect...")
        self.do_lobby()
        print("[-] Lobby ended...\n[-] All players connected.")
        self.words = self.__get_random_words__()
        print("[+] Picked all random words.")
        print("[GAME] Starting game...")
        self.game_loop()
        self.server.close()
        print("[CLOSED] Game closed.")
       
    def do_lobby(self):
        """
        Lobby - Waits for players until first player is ready or until max player limit is reached.
        """
        try:
            # Create server and bind it to port.
            self.server.bind(('', self.port))
        except:
            raise Exception("Could not start server...")
        
        # Bind server 
        self.server.listen(2) 
        self.servers = [self.server]
        self.start_game = False
        
        print(self.players)
        # Loop until either game starts or player limit is reached
        while len(self.players) < self.player_limit and not self.start_game: 
            player_connections = [player.conn for player in self.players]
            temp_servers       = [self.server] + player_connections
            read, _, _ = select(temp_servers, [] , [])
            for serv in read:
                if serv is self.server:
                    self.accept_connection(serv)
                elif self.__in_players__(serv):
                    self.accept_input(serv)
        
    def __get_random_words__(self):
        """
        Picks 3 random words from a wordlist(word_list.txt)
        """
        with open("word_list.txt", "r") as f :
            text = f.read().splitlines()
            for _ in range(self.max_rounds):
                words = []
                for _ in range(3):
                    words.append(choice(text))
                yield words 
    

    def filter_drawers(self):
        """
        Makes sure all the drawers are in the game and not disconnected.
        """
        if len(self.players) <= 1 : handler(1,1)
        
        connections = [player.conn for player in self.players]
        rd, _, _ = select(connections, [], [])
        for sock in rd:
            dt = sock.recv(512, socket.MSG_PEEK)
            # Check if player is disconnected.
            if len(dt) == 0:
                self.drawers.remove(sock)
                self.players.remove(sock)
                

    def pick_drawer(self):
        """
        Picks a drawer for the current round.
        """
        drawer = choice(self.drawers) # Chooses random drawer out of the drawers
        self.drawers.remove(drawer)
        return drawer

    def __cast__(self, player, ability_name):
        """
        @player         = Player casting the ability
        @ability_name   = Ability's name

        return: error_text, is_successful
        """
        for ability in player.abilities:
            if ability.name == ability_name:
                casted_ability = ability
        if (player.mana < casted_ability.cost):
            return "Not enough mana", False
        if (not casted_ability.cast()):
            return "This ability is on cooldown", False
        
        print("[CAST] {} has been casted by {}".format(ability_name, player.name))
        self.broadcast("{} ability has been casted by {}")
        ability_name = ability_name.lower()
        if (ability_name == "blind_team"):
            for cur_player in self.players:
                if (cur_player != player):
                    # Set player state and remove 
                    cur_player.add_state(ability_name)
                    remove_state_timer = Timer(casted_ability.time_lasting, cur_player.remove_state, [ability_name])
                    remove_state_timer.start()
        elif (ability_name == "unblind"):
            player.remove_state(ability_name)
        elif (ability_name == "blind_person"):
            # Make prompt pop up and get player's name
            pass


    
        return "OK", True
    
 

    def execute_round(self, round):
        """
        Executes a new round.
        """
        self.round = round
        self.picked_word = False
        self.started_guessing = False
        self.round_words = next(self.words)
        self.reset_board()
        
        # Get all player connections 
        self.filter_drawers()
        connections = [player.conn for player in self.players]
        if (len(self.drawers) == 0):
            self.drawers = connections
        self.drawer = self.pick_drawer()
        
        # Broadcast round beginning
        self.broadcast("chat Round_{}_is_beginning_and_{}({})_is_the_drawer".format(self.round, self.drawer.name, self.drawer.ip))
        self.pick_word()
        
        # Start timer, allow drawing player to send images to server
        img = Image.new('RGB', (400, 400), (255, 255, 255))
        img.save("round{}.png".format(str(self.round)), "PNG")

        start_time = time.time() # Round starting time
        self.broadcast("chat Round_{}_is_starting!_You_have_60_seconds_to_guess_the_word!".format(self.round))
        self.started_guessing = True

        # Looping until 1. Word gets guessed || 2. 60 Seconds have passed.
        while True:
            self.filter_drawers()
            connections = [player.conn for player in self.players]
            rd, _, _ = select(connections, [], [])
            for player in rd:
                self.accept_input(player) 

            end_time = time.time()
            if (end_time - start_time > 60):
                self.broadcast("chat Round_ended!_No_one_guessed_the_correct_word")
                break

    def pick_word(self):
        """
        Lets the artist choose a word out of three words
        """
        # Let the drawer know he has 30 seconds and send him the list of words.
        self.drawer.conn.send("chat You_have_30_seconds_to_pick_a_word")
        self.drawer.conn.send("pick " + '_'.join(self.round_words))   
        cur_time = time.time()
        
        # Loop until 1. The drawer picks a word || 2. 30 Seconds have been passed.
        while not self.picked_word:
            self.filter_drawers()
            connections = [player.conn for player in self.players]
            rd, _, _ = select(connections, [], [])
            for sock in rd:
                self.accept_input(sock)

            end_time = time.time()    
            if (end_time - cur_time > 30):
                self.round_words = choice(self.round_words)
                self.broadcast("chat The_drawer_hasn\'t_picked_a_word,_so_{}_has_been_picked_automatically".format(self.round_words))
                break

    def reset_board(self):
        """
        Resets each client's board and sends a white board.
        """
        for client in self.players:
            self.send_image(client.conn, "canvas.png")
            
    def game_loop(self):
        """
        Main game loop
        """
        for round in range(1, self.max_rounds + 1):
            self.execute_round(round)
        
        # Get final results.
        self.sort_players()
        self.send_results()
    
    def send_results(self):
        winner_name = self.players[0].name
        winner_IP = self.players[0].ip
        winner_score = self.players[0].score
        print("Players : \{")
        print("\t{}({}) : {},".format(winner_name, winner_IP, winner_score))
        self.broadcast("chat {}({})_has_won_the_game_with_{}_points".format(winner_name, winner_IP, winner_score))
        for player in self.players[1:]:
            print("\t{}({}) : {},".format(winner_name, winner_IP, winner_score))
        print("\}")
        
    def sort_players(self):
        """
        Sorts the `self.players` list by max score
        """
        self.players = sorted(self.players, key=lambda x: x.score)
        
    def receive_image(self):
        """
        Receiving the canvas from the drawing client.
        """
        self.canvas = ""
        self.receiving_image = True
        
        # Loop until finished getting image
        while self.receiving_image:
            connections = [player.conn for player in self.players]
            rd, _, _ = select(connections, [], [])
            for sock in rd:
                self.accept_input(sock)
        print("[IMAGE] Received new canvas by DRAWER({})".format(self.drawer.ip))
		
    def send_image(self, client, image_name):
        """
        Sends an image(canvas) through a socket
         SERVER............................CLIENT
                 SEND IMAGE CONFIRMATION
            ---------------------------------> 
                 READY TO RECEIVE IMAGE 
            <--------------------------------- 
                      TRANSFER IMAGE
            ---------------------------------> 
        """ 
        message_size = 1024
        file_path = os.getcwd() + "/" + image_name
        file_size = int((os.path.getsize(file_path) + message_size - 1) / message_size)
        file_format = os.path.splitext(file_path)[1]

        #                               BLOCK COUNT    FILE FORMAT      BLOCK SIZE
        file_prop = "{} {} {}".format(str(file_size), file_format, str(message_size))
        block_count, file_format, block_size = str(file_size), file_format, str(message_size)
        
        client.setblocking(1)
        client.send(str(file_prop))
        data = client.recv(1024)
        if (data and data.startswith("RECV")):
            print("[+] Sending " + str(file_size) + " parts...")
            file_content = ""
            with open(file_path, "rb") as f:
                byt = f.read(1)
                while (byt != ""):
                    file_content += byt
                    byt = f.read(1)
            
            for i in range(1, file_size + 1):
                self.filter_drawers()
                if (not self.__in_players__(client)): return
                client.send(file_content[:i * message_size])
                file_content = file_content[i * message_size:]
            if file_content:
                client.send(file_content)
            

    def accept_connection(self, serv):
        """
        Handles new connection attempts.
        """
        conn, addr = serv.accept()
        print("[-] Player({}) is attempting to connect...".format(str(addr[0])))
        if (not self.__in_players__(None , addr)):
            print("\t[+] Player({}) is now connected.".format(str(addr[0])))
            conn.setblocking(0) # In order for the .recv() to not block
            
            abilities = [] 
            abilities.append(Ability(2 * len(self.players), "blind_team", 10, 4)) # Cost, name, cooldown, effect time
            abilities.append(Ability(5, "unblind", 20, 0)) # Cost, name, cooldown
            abilities.append(Ability(2, "blind_person", 3, 4))

            player = Player(conn, 10, None, abilities, addr[0])
            self.players.append(player)
        else:
            print("\t[+] Player({}) is already connected from this IP.".format(str(addr[0])))
            conn.send("Already connected from this IP...")
            conn.close()

    def broadcast(self, msg, fromSocket=None):
        """
        Broadcasts a message to every socket except fromSocket
        """
        for player in self.players:
            conn = player.conn
            if conn is not fromSocket:
                conn.send(msg)

    def is_valid(self, input):
        """
        Checks if given input is valid or not
        """
        valid_commands = ['chat', 'change_canvas', 'username'] # Pick is sent from the server
        first_word = input.split(' ')[0]
        return first_word in valid_commands

    def accept_input(self, serv):
        """
        Handles the input gives by the players
        """
        data = serv.recv(1024) # Looks like this: {command} sentence : Example chat start
        
        # Player data 
        player = self.__get_player__(serv)
        player_IP = player.ip
        player_name = player.name
        
        # Check if the data isn't empty (means the client disconnected)
        if data:
            split_data = data.split(' ') # Should be in the form of: [{command}, sentence]
            if (len(split_data) < 2): return
            command = split_data[0].lower()
            message = split_data[1].lower()
            print("[INPUT] Received input from {}({}) : {}".format(str(player_name), player_IP, data))
            if (not self.is_valid(command)):
                print("[INPUT] Received invalid input")
                return 
            if command == "username" and not self.start_game:
                if player_name == None and command == "username":
                    for player in self.players:
                        if (player.name == message):
                            return
                    print("Set username for player {}".format(player_IP))
                    player.name = message
                        
            elif command == "chat":
                if not self.start_game:
                    # Loading screen runs until 1. Player limit is reached || 2. First player to join types start
                    self.broadcast(data, serv)
                    if player == self.players[0] and message == "start":
                        self.start_game = True
                   
                elif not self.picked_word and player.conn == self.drawer.conn:
                    """
                    Word picking phase, the drawer picks a word
                    """
                    if message in self.round_words:
                        # Word has been picked
                        self.round_words = message
                        self.picked_word = True
                        self.broadcast("chat {}({})_has_picked_the_word:_{}".format(player_name, player_IP, message))
                        print("[GAME] {}({}) has picked a word! {}".format(player_name, player_IP, message))
                        
                elif self.started_guessing and not player.conn == self.drawer.conn:
                    """
                    Getting a guess from one of the players.
                    """
                    if message == self.round_words:
                        self.broadcast("chat {}({})_has_guessed_the_correct_word!".format(player_name, player_IP))
                        self.broadcast("chat The_correct_word_was_{}".format(self.round_words))
                        self.started_guessing = False
                    else:
                        self.broadcast(data, serv)
                
                else:
                    # Broadcasting the chat messages if no other condition is hit.
                    self.broadcast(data, serv)
                    
            elif not self.receiving_image and command == "canvas_change":
                if player.conn == self.drawer.conn:
                    """
                    Sending canvas change to all players(except drawers since he already has the canvas)
                    """
                    # Receive image + how many chunks of the image are being sent.
                    self.receiving_times = message
                    self.receive_image()
                    
                    # Sending canvas change to all players.
                    print("[+] Sending canvas change to players...")
                    for player in self.players:
                        if player.conn == self.drawer.conn: continue
                        self.send_image(player.conn, "round{}".format(self.round))
                    self.receiving_image = False
                    print("\t[-] Finished sending canvas to players.")
            else:
                if self.receiving_image and player.conn == self.drawer.conn:
                    """
                    Receive another chunk of the canvas, and set the receive amount to 1 less.
                    """
                    self.receiving_times -= 1
                    self.canvas += data
                    self.receiving_image = self.receiving_times != 0

        else:
            """
            Handling player disconnections
            """
            print("\t\t[-] Player {}({}) has disconnected...".format(player_name, player_IP))
            self.__remove_player__(serv)
            serv.close()
            
    def __remove_player__(self, conn):
        for i, player in enumerate(self.players):
            if (player.conn == conn):
                del self.players[i]
                break
                
    def __get_player__(self, conn):
        """
        Getting player from player list(`self.player`) by connection.
        """
        for i, player in enumerate(self.players):
            if player.conn == conn:
                return player 
        return None
    
    def __in_players__(self,conn=None, addr=None):
        """
        Checks if a player is in the player array
        """
        if addr is not None:
            for player in self.players:
                if (player.ip == addr[0]):
                    return True
        elif conn is not None:
            for player in self.players:
                if (player.conn is conn):
                    return True
        return False

        
def erase_rounds():
    """
    Erasing all round{}.png images saved.
    """
    global MAX_ROUNDS
    print("[ERASE] Cleaning up round canvases...")
    for i in range(1, MAX_ROUNDS + 1):
        round_pic = "round{}.png".format(str(i))
        if (os.path.isfile(round_pic)):
            os.remove(round_pic)
            print("\t\t[-] Erased photo {} from {}".format(round_pic, os.getcwd()))
    print("\t[ERASE] Done cleaning up round canvases.")

class ServiceExit(Exception):
    pass

def handler(signum, frame):
    """
    Handling SIGINT(CTRL + C) incase admin wants to shutdown server.
    """
    raise ServiceExit("ServiceExit")
        
def main():
    print("Starting program...")
    signal.signal(signal.SIGINT, handler)
    try:
        game = Game(8080, 5, 10)
    except ServiceExit:
        print("Exiting...")
        sys.exit(0)
if __name__ == "__main__":
    main()
