"""
Program description:
This is a server for a draw my thing game made by Guy and Yoav.

TODO: 
1. Think of new abilities
2. Try playing
"""
from threading import Timer
import socket, signal, time, re, os
from PIL import Image, ImageDraw
from random import choice
from select import select
from sys import exit

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
        elif (curtime - self.last_used >= self.cooldown):
            self.last_used = curtime
            return True
        return False
    

class Player(object):
    """
    Represents a player.
    @score      = A player's score                  (int type)
    @conn       = A player's socket connection      (socket type)
    @name       = A player's name                   (string type)
    @abilities  = A player's abilities              (list of abilities class type)
    @ip         = A player's IP                     (string type)
    @state      = A variable that represents        (int type)
                  effects from casted spells
    """
    def __init__(self, conn, name, ip, player_count):
        self.name       = name
        self.abilities  = []
        self.conn       = conn 
        self.score      = 10 # Should be 0 TODO 
        self.ip         = ip
        self.time_unblind = None
        self.state      = 0 # State is represented by each bit of the number
        # 0           0      0          0       0           0           0           0
        # Blind      Blind   Disable    Give      
        # specific   Team    Typing     Letter
        # person             Specific

        # Add abilities to each player's kit
        self.__create_abilities__(player_count)

    def __repr__(self):
        return "{}: [\nscore: {}\nip: {},\nstate: {},\nabilities: [\n\t\t{}\n]\n]".format(self.name, self.score, self.ip, self.state, self.abilities)
    def __create_abilities__(self, player_count):
            
        self.abilities.append(Ability(2 * player_count, "blindteam", 10, 4)) # Cost, name, cooldown, effect time
        self.abilities.append(Ability(5, "unblind", 20, 0)) # Cost, name, cooldown
        self.abilities.append(Ability(2, "blindperson", 3, 4))


    def __get_ability__(self, ability_name):
        # Get ability in player's inventory
        for ability in self.abilities:
            if ability.name == ability_name:
                return ability
        return None
 

    def __get_place__(self, state):
        """
        This function receives ability name and returns the ability's place in the 
        `self.state` variable.
        
        @ability_name   = Ability name
        """
        if state == "blind":
            place = 1 << 8
        elif state == "disable": # TODO : REPLACE ABILITY
            place = 1 << 7
        return place 


    def remove_state(self, state):
        """
        This function removes the ability effect from `self.state`

        @ability_name = Ability name
        """
        state = state.lower()
        place = self.__get_place__(state)
        if (self.state & place != 0):
            self.state -= place

        print("[STATE] Removed state {} from {}".format(state, self.name))
    

    def add_state(self, state):
        """
        This function adds an effect to a player.

        @ability_name = Ability name
        """
        state = state.lower()
        place = self.__get_place__(state)
        if (self.state & place == 0):
            self.state += place
        
        print("[STATE] Added state {} to {}".format(state, self.name))
        
    def has_state(self,state):
        
        state = state.lower()
        place = self.__get_place__(state)
        return self.state & place != 0

class Game(object):
        def __repr__(self):
            return "Game : {\nPlayers: %s\nport: %s\n\n}" % (self.players, self.port) 
        
        def handler(self, signum, frame):
            self.server.close()
            raise ServiceExit("ServiceExit")

        def __del__(self):
            print("Shutting down server...")
            #erase_rounds()

        def __init__(self, port, player_limit, max_rounds):
            # Signal to handle CTRL + C, in case owner wants to stop server.
            signal.signal(signal.SIGINT, self.handler)

            self.painting = False 
            # Setting up initial variables
            self.started_guessing = False
            # holds whether word has been picked already by the drawer(bool type)
            self.picked_word = False
            # holds the drawer(Player type)
            self.drawer = None
            # Holds the current drawer's word (array of strings, or string)
            self.drawer_word = []
            # Holds the server port (int type)
            self.port = port
            # Holds a list of drawers(Player[] type)
            self.drawers = []
            # Holds a list of all players(Player[] type)
            self.players = []
            # Holds a list of all players who guessed the drawer_word(Player[] type)
            self.guessed = []
            # Server that hosts the game.
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Variable that holds the maximum amount of players able to play(int type)
            self.player_limit = player_limit
            # Holds amount of rounds to play(int type)
            self.max_rounds = max_rounds
            self.img = Image.new('RGB', (400, 400), "white")

            # Initialize game
            self.__initialize_server__()
            print("Game is running on ({}:{})".format("127.0.0.1", self.port))
            print("[+] Set player limit to {}".format(self.player_limit))
            print("[+] Set max rounds to {}".format(self.max_rounds))
            
            # Initialize lobby
            print("[+] Starting lobby\n [+] Waiting for players to connect...")
            self.do_lobby()
            print("[-] Lobby ended...\n[-] All players connected.")
            
            # Generate word list
            self.words = self.__get_random_words__()
            print("[+] Picked all random words.")

            # Main game
            print("[GAME] Starting game...")
            self.game_loop()

            # Game end
            self.server.close()
            print("[CLOSED] Game closed.")
        

        def __initialize_server__(self):
            """
            This function attempts to bind the `self.server` variable to a port,
            if it fails it raises an Exception.
            """
            
            try:
                # Prevents socket from going into TIME_WAIT at the end of execution.
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                # Binding server to 0.0.0.0 with port (self.port)
                self.server.bind(('', self.port))
            except:
                raise Exception("Could not start server...")
            # Allowing up to 2 connections in a queue
            self.server.listen(2) 

        def do_lobby(self):
            """
            This function is essentially a lobby it waits for players until first player is ready or until max player limit is reached.

            If max player limit is reached, it waits 5 seconds and then starts the game.
            """
            # Holds if the game started.
            self.start_game = False
            # Holds the time the lobby was full.
            cur_time = None
            # Wait amount after lobby is full
            wait_amount = 5 # Seconds

            # Loop until either game starts or player limit is reached
            while not self.start_game: 
                # Get player connections
                player_connections = [player.conn for player in self.players]
                read, _, _ = select([self.server] + player_connections, [] , [], 0)

                for serv in read:
                    # Check if a player is connecting
                    if serv == self.server:
                        self.accept_connection(serv)
                    else:
                        self.accept_input(serv)

                # Check if lobby is full
                if len(self.players) == self.player_limit:
                    if cur_time is None:
                        cur_time = time.time()
                        print("[LOBBY] The maximum amount of players have joined, starting game in 5 seconds...")
                        self.broadcast("chat", "The lobby has been filled. Starting game in 5 seconds...")

                    end_time = time.time()
                    if (end_time - cur_time >= wait_amount): 
                        self.start_game = True
                elif (not cur_time is None):
                    # Check if lobby has been full and now is not full.
                    print("[LOBBY] Cancelled countdown.")
                    self.broadcast("chat", "The countdown has been cancelled")
                    cur_time = None

            self.filter_drawers()

        def __get_random_words__(self):
            """
            Picks 3 random words from a wordlist (word_list.txt)
            to get the words use next().
            """
            
            with open("word_list.txt", "r") as f :
                text = f.read().splitlines()
                for _ in range(self.max_rounds * len(self.players)):
                    words = []
                    # Generate 3 words.
                    for _ in range(3):
                        words.append(choice(text))
                    yield words 
        

        def filter_drawers(self):
            """
            Makes sure all the drawers are in the game and not disconnected or without a name.
            """
            
            # Make sure there is more than 1 player.
            if len(self.players) <= 1: self.handler(1,1)
            
            # Get player connections.
            connections = [player.conn for player in self.players]
            rd, _, _ = select(connections, [], [], 0)
            
            for sock in rd:
                try:
                    data = sock.recv(152, socket.MSG_PEEK)
                except socket.error:
                    self.__remove_player__(sock)
                    return
                player = self.__get_player__(sock)
                # Kick player that disconnected
                if not data:
                    self.__kick_player__(sock, "disconnecting")
                # Kick player that has no name
                elif player.name is None:
                    self.__kick_player__(sock, "not having a name")


        def pick_drawer(self):
            """
            Picks a drawer for the current round from the `self.drawers` list.
            """
            self.filter_drawers()
            drawer = choice(self.drawers) # Chooses random drawer out of the drawers
            self.drawers.remove(drawer)
            return drawer


           
                       
        def execute_round(self, rnd):
            """
            @rnd = round number

            Executes a new round.
            """
            
            self.round = rnd
            self.picked_word = False
            self.started_guessing = False
            self.drawer_disconnected = False
            self.drawer_word = next(self.words)
            self.broadcast("resetboard", "")
            

            # Get all player connections )
            self.filter_drawers()
            if (len(self.drawers) <= 0): return
            self.drawer = self.pick_drawer()
            self.guessed = []
            
            # Current drawer 
            print("[DRAWER] The drawer is {}({})".format(self.drawer.name, self.drawer.ip)) 

            # Broadcast round beginning
            self.broadcast("chat", "Round {} is beginning and {}({}) is the drawer.".format(self.round, self.drawer.name, self.drawer.ip))
            
            print("[WORDS] The picked words are: {}".format(self.drawer_word))        
            self.pick_word()
            if (self.drawer_disconnected):
                self.broadcast("chat", "The drawer has disconnected...")
                return
            self.send_message(self.drawer.conn, "chat", "Your word is {}.".format(self.drawer_word))
            print("[WORD] The picked word is {}".format(self.drawer_word))
            # Start timer, allow drawing player to send images to server
            self.img = Image.new('RGB', (400, 400), "white")
            self.draw = ImageDraw.Draw(self.img)
            #img.save("round{}.png".format(str(self.round)), "PNG")

            start_time = time.time() # Round starting time
            self.broadcast("chat", "Round {} is starting! You have 60 seconds to guess the word!".format(self.round), self.drawer.conn)
            self.started_guessing = True

            # Send word template, for example: "Family home" = "6 4" => "______ ____"
            string_lengths = []
            for word in self.drawer_word.split(" "):
                string_lengths.append(str(len(word)))
            self.broadcast("word", "_".join(string_lengths))

            # Looping until 1. Word gets guessed || 2. 60 Seconds have passed.
            while self.started_guessing and not self.drawer_disconnected:
                self.filter_drawers()
                connections = [player.conn for player in self.players]
                rd, _, _ = select(connections, [], [], 0)
                for player in rd:
                    self.accept_input(player) 

                end_time = time.time()
                if (self.drawer_disconnected):
                    break
                if (len(self.guessed) == len(self.players) - 1):
                    self.broadcast("chat", "Everyone guessed the correct word!")
                    break
                elif (end_time - start_time > 60):
                    if (len(self.guessed) == 0):
                        self.broadcast("chat", "Round ended! No one guessed the correct word.")
                    else:
                        self.broadcast("chat", "Round ended! Correct guessers: {}".format([player.name for player in self.guessed]))
                    break
            if (self.drawer_disconnected):
                self.broadcast("chat", "The drawer has disconnected...")
                return
            self.broadcast("chat", "The correct word was: {}".format(self.drawer_word))

            # Score delivery
            # 1st guesser = 4
            # 2nd guesser = 3
            # 3rd guesser = 2
            # ...         = 1
            for i, player in enumerate(self.guessed):
                if i + 1 == 1:
                    self.send_message(player.conn, "chat", "You have received 4 points for being the first to guess the word!")
                    player.score += 4
                elif i + 1 == 2:
                    self.send_message(player.conn, "chat", "You have received 3 points for being the second to guess the word!")
                    player.score += 3
                elif i + 1 == 3:
                    self.send_message(player.conn, "chat", "You have received 2 points for being the third to guess the word!")
                    player.score += 2
                else:
                    self.send_message(player.conn, "chat", "You have received 1 point for correctly guessing the word!")
                    player.score += 1
            self.send_players()

        def pick_word(self):
            """
            Lets the artist choose a word out of three words
            """
            if (not self.drawer in self.players): return
            # Let the drawer know he has 30 seconds and send him the list of words.
            self.drawer.conn.send("chat You_have_30_seconds_to_pick_a_word\n\r")
            self.drawer.conn.send("chat Pick:_" + '_'.join(self.drawer_word) + "\n\r")   
            cur_time = time.time()
            
            # Loop until 1. The drawer picks a word || 2. 30 Seconds have been passed.
            while not self.picked_word and not self.drawer_disconnected:
                self.filter_drawers()
                connections = [player.conn for player in self.players]
                rd, _, _ = select(connections, [], [], 0)
                for sock in rd:
                    self.accept_input(sock)

                end_time = time.time() 
                if (end_time - cur_time > 30):
                    self.drawer_word = choice(self.drawer_word)
                    self.broadcast("chat", "The drawer hasn\'t picked a word, so a word has been picked randomly.".format(self.drawer_word))
                    print("[GAME] {}({}) hasn\'t picked a word so the word {} has been chosen randomly.".format(player.name, player.ip, self.drawer_word))
                    break
            else:
                # In case the drawer picked a word
                print("[GAME] {}({}) has picked a word! {}".format(self.drawer.name, self.drawer.ip, self.drawer_word))

                
        def game_loop(self):
            """
            Main game loop
            """
            self.send_players()
            for rnd in range(1, self.max_rounds + 1):
                print("===========================")
                print("          ROUND {}         ".format(rnd))
                print("===========================")
                self.drawers = [player for player in self.players]
                while len(self.drawers) != 0:
                    self.execute_round(rnd)
                    print("---------------------------")

            # Get final results.
            self.sort_players()
            self.send_results()
        
        def send_results(self):
            winner_name = self.players[-1].name
            winner_IP = self.players[-1].ip
            winner_score = self.players[-1].score
            print("Players : {")
            print("\t{}({}) : {},".format(winner_name, winner_IP, winner_score))
            for player in (self.players[:-1])[::-1]:
                print("\t{}({}) : {},".format(player.name, player.ip, player.score))
            print("}")
            self.broadcast("chat", "{}({}) has won the game with {} points!".format(winner_name, winner_IP, winner_score))
        
        def cast(self, ability_name, player, info=""):
            ability_name = ability_name.lower()
            # Validate cast
            message, success = self.__cast__(ability_name, player, info)
            if (success == False):
                print("[CAST] Failed cast by {} for {}".format(player.name, message))
                self.send_message(player.conn, "chat", message)
                return

            print("[CAST] {} has been casted by {}".format(ability_name, player.name))
            self.broadcast("chat", "{} ability has been casted by {}".format(ability_name, player.name)) 
            casted_ability = player.__get_ability__(ability_name)
            if (ability_name == "blindteam"):
                for cur_player in self.players:
                    if (cur_player != player and cur_player != self.drawer):
                        # Set player state and remove 

                        if (not cur_player.has_state("blind")): continue
                        cur_player.add_state("blind")
                        cur_player.time_unblind = time.time() + casted_ability.time_last
                        remove_state_timer = Timer(casted_ability.time_last, cur_player.remove_state, ["blind"])
                        remove_state_timer.start()

            elif (ability_name == "blindperson"):
                # Make prompt pop up and get player's name
                pass

        def __cast__(self, ability_name, player, info=""):
            """
            This function checks if a player can cast an ability.

            @player         = Player casting the ability. (Player type)
            @ability_name   = Ability's name.             (Ability type)
            @info           = Optional, might include affected player's name. (string type)

            return: error_text, is_successful
            """

            
            ability_name = ability_name.lower()
            casted_ability = player.__get_ability__(ability_name)
            if (casted_ability is None):
                return "No such ability exists", False
            # Check if player has enough points to cast the spell
            if (player.score < casted_ability.cost):
                return "Not enough mana", False
            
            username_abilities = ["disabletyping", "blindperson"]
            if ability_name in username_abilities:
                if player.name == info or player.name == self.drawer.name:
                    return "Can't cast the ability on yourself or on the drawer", False
                for ply in players:
                    if ply.name == info:
                        if ply.has_state("blind"):
                            return "Cannot blind player with blindness", False
                        break
                else:
                    return "No player with such nickname", False

            if (not casted_ability.cast()):
                return "This ability is on cooldown", False
            
            player.score -= casted_ability.cost
            return "OK", True
         
        def sort_players(self):
            """
            Sorts the `self.players` list by max score
            """
            self.players = sorted(self.players, key=lambda x: x.score)
        
        def send_players(self):
            players_score = ""
            for player in self.players:
                players_score += "{},{} ".format(player.name, player.score)
            self.broadcast("getplayers", players_score[:-1], None, False)

        """
        def receive_image(self):
            
            Receiving the canvas from the drawing client.
            
            self.canvas = ""
            self.receiving_image = True
            
            # Loop until finished getting image
            while self.receiving_image:
                connections = [player.conn for player in self.players]
                rd, _, _ = select(connections, [], [])
                for sock in rd:
                    self.accept_input(sock)
            print("[IMAGE] Received new canvas by DRAWER({})".format(self.drawer.ip))
         
        def send_image(self, client):
            
            Sends an image(canvas) through a socket
             SERVER............................CLIENT
                     SEND IMAGE CONFIRMATION
                ---------------------------------> 
                     READY TO RECEIVE IMAGE 
                <--------------------------------- 
                         TRANSFER IMAGE
                ---------------------------------> 
            
            message_size = 1024
            
            while self.painting: pass	
            self.img.save("image.png", "PNG")
            
            file_path = os.getcwd() + "/image.png"	
            image = open(file_path, "rb") 
            content = image.read()
            
            file_size = int((len(content) + message_size - 1) / message_size)
            file_format = "png"

            #                                         BLOCK COUNT    FILE FORMAT      BLOCK SIZE
            file_prop = "canvas_change {} {} {}\n\r".format(str(file_size), file_format, str(message_size + len("IMG ") + len("\n\r")))
            block_count, file_format, block_size = str(file_size), file_format, str(message_size)
            
            client.conn.send(str(file_prop))
            #self.img.show()	
            for i in range(1, file_size + 1):
                self.filter_drawers()
                if (not self.__in_players__(client.conn)): return
                client.conn.send("IMG " + content[:i * message_size] + "\n\r")
                content = content[i * message_size:]

            if content:
                    client.conn.send("IMG " + content + "\n\r")
        """
        def accept_connection(self, serv):
            """
            @serv = socket of server

            Handles new connection attempts.
            """
            conn, addr = serv.accept()
            print("[-] Player({}) is attempting to connect...".format(str(addr[0])))
            
            if (len(self.players) == self.player_limit):
                conn.send("Lobby filled. cannot join")
                conn.close()
            
            if self.start_game:
                conn.send("Game already started.")
                conn.close()

            if True: #(not self.__in_players__(None , addr)):
                print("\t[+] Player({}) is now connected.".format(str(addr[0])))
                conn.setblocking(0) # In order for the .recv() to not block
                    
                player = Player(conn, None, addr[0], len(self.players) + 1)
                self.players.append(player)
            else:
                print("\t[+] Player({}) is already connected from this IP.".format(str(addr[0])))
                conn.send("Already connected from this IP...")
                conn.close()

        def broadcast(self, command, msg, fromSocket=None, removeSpaces=True):
            """
            @msg        = the message to broadcast
            @fromSocket = the socket not to send the message to

            Broadcasts a message to every socket except fromSocket
            """
            if removeSpaces:
                msg = "_".join(msg.split(' '))
            for player in self.players:
                conn = player.conn
                if conn is not fromSocket:
                    if msg != "":
                        conn.send("{} {}\n\r".format(command, msg))
                    else:
                        conn.send("{}\n\r".format(command))
        def is_valid(self, inp):
            """
            @inp = input to be validated

            True: inp is in the form "{command} something"
            False: otherwise
            Checks if given input is valid or not
            """
            valid_commands = ['chat', 'canvas_change', 'username', 'cast'] # Pick is sent from the server
            first_word = inp.split(' ')[0]
            return first_word in valid_commands

        def __accept_input__(self, sock, command):
            """
            @sock    = socket to receive data from.
            @command = which command the user uses.(should be valid, except when receiving image)

            This function accepts data smaller than 150 characters, and kicks the socket otherwise.
            This function reads data until "\n\r" and returns the data or None incase invalid data.
            """
            if (self.__get_player__(sock) is None): return None
            end = "\n\r"
            hit = 0
            data = ""
            allowed = 152
            command = command.lower()
            if (command == "username"):
                allowed = 20 + len("username ")
            elif (command == "chat"):
                allowed = 150 + len("chat ")
            elif (command == "canvas_change"):
                allowed = 2048 + len("canvas_change ")
            elif (command == "cast"):
                allowed = 60 + len("cast ")
            #elif self.receiving_message:
            #    allowed = 1048
            else:
                allowed = 150
            peek_data = sock.recv(allowed, socket.MSG_PEEK)
            if end not in peek_data:
                self.__kick_player__(sock, "sending more than character limit or not having \\n\\r at the end of the line.")
                print("KICKING")
                return None

            while (hit < len(end)):
                char = sock.recv(1)
                if (char != end[hit]):
                    hit = 0
                if (char == end[hit]): 
                    hit += 1
                data += char
            return data

        def send_message(self, serv, command, message, replace_spaces=True):
            if (self.__get_player__(serv) is None): return
            if replace_spaces:
                message = "_".join(message.split(' '))
            serv.send("{} {}\n\r".format(command, message))

        def accept_input(self, serv):
            """
            @serv = socket to accept input from

            Handles the input gives by the players
            """
            # Receive data
            data = serv.recv(20, socket.MSG_PEEK) # Looks like this: {command} sentence : Example chat start
            # Player data 
            player = self.__get_player__(serv) 
            if not data:
                """
                Handling player disconnections
                """
                if player == self.drawer:
                    self.started_guessing = False
                print("\t[-] Player {}({}) has disconnected...".format(player.name, player.ip))
                self.__remove_player__(serv)
                serv.close()
                return

            command_temp = data.split(' ')[0] 
            data = self.__accept_input__(serv, command_temp) 
            if data is None: return
            data = data.strip("\n\r")
          
            
            # Check if the data isn't empty (means the client disconnected) 
            split_data = data.split(' ') # Should be in the form of: [{command}, sentence]
            if (len(split_data) < 2): return
            if (len(data) > 40):
                pass
                #print("[INPUT] Received long input from {}({})".format(str(player.name), player.ip))
            else:
                print("[INPUT] Received input from {}({}) : {}".format(str(player.name), player.ip, data))

            # Regex patterns for certain commands
            regex_username      = r"^username [a-z0-9]{1,20}$"
            regex_chat          = r"^chat [a-zA-Z0-9_,.?'!]{1,150}$"
            regex_canvas_change = r"^canvas_change [a-z0-9]{6} [0-9]{1,2} ([0-9]{1,3},[0-9]{1,3} )+$"
            regex_cast          = r"^cast [a-z]{1,20}$"
            regex_cast_2        = r"^cast [a-z]{1,20} [a-z0-9]{1,20}$"
            
            if re.match(regex_username, data):
                if (self.start_game):
                    print("Player is trying to change username, even though game started")
                    return
                if (not player.name is None):
                    print("Player trying to change username even though he has one")
                    return

                message = split_data[1].strip(" ")
                regex = r"^[a-z0-9]{1,20}$"
                if (not re.match(regex, message)):
                    self.send_message(serv, "chat", "Your name needs to have only alphabetical characters and numbers from 0 to 9(only lowercase)")
                    return
                
                for player in self.players:
                    if (player.name == message):
                        self.send_message(serv, "chat", "Another player has this name. Please choose another name.")
                        return
                
                print("Set username for player {} : {}".format(player.ip, message))
                player.name = message
                        
            elif re.match(regex_chat, data):
                message = split_data[1]
                message = " ".join(message.split("_")).strip(" ")
                regex = r"^[a-zA-Z0-9 ,.?'!]{1,150}$"
                if (not re.match(regex, message)):
                    self.send_message(serv, "chat", "Your message has invalid characters.")
                    return

                if not self.start_game:
                    if player == self.players[0] and message == "start":
                        self.start_game = True
                   
                elif not self.picked_word and player.conn == self.drawer.conn:
                    """
                    Word picking phase, the drawer picks a word
                    """
                    if message in self.drawer_word:
                        # Word has been picked
                        self.drawer_word = message
                        self.picked_word = True
                        return 
                        
                elif self.started_guessing and (player.conn != self.drawer.conn and message == self.drawer_word):
                    """
                    Getting a guess from one of the players.
                    """
                    self.broadcast("chat", "{}({}) has guessed the correct word!".format(player.name, player.ip))
                    self.guessed.append(player)
                   
                    return

                elif self.started_guessing and player.conn == self.drawer.conn:
                    self.send_message(player.conn, "chat", "You are the drawer, you cannot type in chat.")
                    return
                
                self.broadcast("chat", "{}: {}".format(player.name, message), serv)

            elif re.match(regex_canvas_change, data + " "):
                if (not self.started_guessing):
                    print("Trying to change canvas before guessing began")
                    return
                if (self.drawer.conn != serv):
                    print("Non-drawing player is trying to change the canvas")
                    return
                """
                @message = list of coordinates

                Getting a list of coordinates to change + color
                """
                # canvas_change 250,300,E555D 100,50,E5E5E
                message = split_data[3:] # "250,300", "100,50", "70,90"
                color   = split_data[1]
                width   = int(split_data[2])
                self.__paint_coordinates__(serv, message, color, width) 
                #for player in self.players:
                    #self.send_image(player)

            elif (re.match(regex_cast, data) or re.match(regex_cast_2, data)):
                if (not self.started_guessing):
                    print("Trying to cast spell before guessing began")
                    return
                if (self.drawer.conn == serv):
                    print("Drawer is trying to cast a spell")
                    return
                regex = "^cast [a-z]{1,20}(?(?= )( [a-z0-9]{1,20}))$"
                ability_name = split_data[1].lower().strip(" ")
                info = ""
                if (len(split_data) == 3): info = split_data[2]
                self.cast(ability_name, player, info)
                
            else:
                print("[INPUT] Invalid input : {}".format(data))
                
            
            """
            elif not self.receiving_image and command == "canvas_change":
                if player.conn == self.drawer.conn:
                    
                    @message = number of times to accept

                    Sending canvas change to all players(except drawers since he already has the canvas)
                    
                    # Receive image + how many chunks of the image are being sent.
                    self.receiving_times = int(message)
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
                    
                    Receive another chunk of the canvas, and set the receive amount to 1 less.
                    
                    self.receiving_times -= 1
                    self.canvas += data
                    self.receiving_image = self.receiving_times != 0
           """
        
        def __paint_coordinates__(self, player, coordinate_array, color, width):
		"""
		Paints coordinates given.

		@player           = player who painted the pixels
		@coordinate_array = coordinates to paint with color : ["20,100,d5d5d5"]
		"""
		
		# Test coordinate validity
		regex = r"^[0-9]{1,3},[0-9]{1,3}$"
		#regex = r"^(([0-9]{1,3},){2}[a-zA-Z0-9]{6})$"

		# Coordinate array (row,col)
		cords = [] 
		# Validate coordinates
		for cord in coordinate_array:
		    if (not re.match(regex, cord)):
		        self.send_message(player, "chat", "Sent invalid coordinates.")
		        return
		    split_coordinate = cord.split(",") # [250, 300]
		    temp_cords = [int(x) for x in split_coordinate[:2]] # [250, 300]
		    for i in temp_cords:
		        if i >= 400 or i < 0:
		            self.send_message(player, "chat", "Sent invalid coordinates.")
		            return

		    cords.append(tuple(temp_cords))
		# turn coordinates to int
		cords = [(int(cord[0]), int(cord[1])) for cord in cords]
		#RGBColors = []
		# Change hex color to RGB color
		"""
		for color in colors:
		    RGBColors.append((int(color[:2], 16), int(color[2:4], 16),int(color[4:], 16), 255))
		"""
		# Put pixel in image
		for i, cord in enumerate(cords[:-1]):
		    next_cord = cords[i+1]        
		    self.draw.line((cord, next_cord), fill="#{}".format(color), width=width)
                #self.img.show() 
		for cur_player in self.players:
		    if cur_player.has_state("blind"):
		            Timer(cur_player.time_unblind - time.time(), self.send_message, [cur_player.conn, "canvas_change", "{} {} {}".format(color, str(width), " ".join(coordinate_array)), False])
		    else:
		        self.send_message(cur_player.conn, "canvas_change", "{} {} {}".format(color, str(width), " ".join(coordinate_array)), False)
 
        def __kick_player__(self, conn, reason):
            """
            This function kicks out / disconnects a player.
            
            @conn       = connection to disconnect.
            @reason     = kicking reason.
            """
            
            player = self.__get_player__(conn)
            print("[KICK] kicking player {}({}) for {}".format(player.name, player.ip, reason))
            self.__remove_player__(conn)
            conn.close()


        def __remove_player__(self, conn):
            """
            This function removes a player from self.players and self.drawers list

            @conn       = connection to remove.
            """
            for player in self.players:
                if (player.conn == conn):
                    self.players.remove(player)
                    if (player in self.drawers):
                        self.drawers.remove(player)
                    if (player == self.drawer):
                        self.drawer_disconnected = True        
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
                    if (player.conn == conn):
                        return True
            return False

"""    
def erase_rounds():
    
    Erasing all round{}.png images saved.
    
    global MAX_ROUNDS
    print("[ERASE] Cleaning up round canvases...")
    for i in range(1, MAX_ROUNDS + 1):
        round_pic = "round{}.png".format(str(i))
        if (os.path.isfile(round_pic)):
            os.remove(round_pic)
            print("\t\t[-] Erased photo {} from {}".format(round_pic, os.getcwd()))
    print("\t[ERASE] Done cleaning up round canvases.")
"""
class RangeError(Exception):
    pass

class ServiceExit(Exception):
    pass

"""
def handler(signum, frame):
    
    Handling SIGINT(CTRL + C) incase admin wants to shutdown server.
    
    raise ServiceExit("ServiceExit")
"""

def main():
    print("Starting program...")
    # signal.signal(signal.SIGINT, handler)
    try:
        # get port
        port = raw_input("Port: ")
        
        # validate port
        try:
            port = int(port)
            if (port < 0 or port > 65535):
                raise RangeError("")
        except ValueError:
            print("The port needs to be a number")
            exit(1)
        except RangeError:
            print("The port needs to be between 0 <= port <= 65535")
            exit(1)
        
        
        # get player limit
        player_limit = raw_input("Player Limit: ")
        try: 
            player_limit = int(player_limit)
            if (player_limit < 2):
                print("Player limit has to be larger than 1")
                exit(1)
        except ValueError:
            print("Player limit is a number")
            exit(1)

        # get max round number
        max_round = raw_input("Rounds: ")
        try:
            max_round = int(max_round)
        except ValueError:
            print("Max round must be a number")
            exit(1)
    
        # Launch game
        game = Game(port, player_limit, max_round)

    except ServiceExit:
        print("Exiting...")

if __name__ == "__main__":
    main()
