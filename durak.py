import numpy as np
from random import shuffle
from copy import deepcopy
from time import sleep
from random import randint
suit_str_dict = {0: "Hearts", 1: "Diamonds", 2: "Clubs", 3: "Spades"}
DECK_SIZE_N_VALS = DSNV = 8

DECK_SIZE = DS = DECK_SIZE_N_VALS * 4
val_str_dict = { DSNV: "Ace", DSNV-1: "King", DSNV - 2: "Queen", DSNV - 3: "Jack"}
i = 4
v = 10
while DSNV - i > -1:
    val_str_dict[DSNV-i] = str(v)
    v += -1
    i += 1

class Card:
    #suit: 0, 1, 2, 3
    def __init__(self,suit,val):
        self.suit = int(suit)
        self.val = int(val)
    @property
    def mat(self):
        mat = np.zeros([4,DECK_SIZE_N_VALS],int)
        mat[self.suit][self.val] = 1
            #return a matrix (suits x values)
            #with a one in the place corresponding to the card 
        return mat
    def __str__(self):
        return f"{val_str_dict[self.val]} of {suit_str_dict[self.suit]}"
    def __eq__(self,other):
        if self.suit == other.suit and self.val == other.val: return True
        else: return False

def card_i(i): #get card by absolute value (cards arranged in order by value within suit
    return Card( suit = np.floor( i / DECK_SIZE_N_VALS), val = int(i%DECK_SIZE_N_VALS) )
def i_card(card): #get absolute value of card
    return DECK_SIZE_N_VALS*card.suit + card.val
#it's really just a fancy list...
class Hand: #it holds cards. The deck is a hand. Piles are hands. Players are hands.
    def __init__(self, deck = None, name = "HAND"):
        self.name = name
        if deck == None:
            self.cards = [] #empty
            return
        self.cards = [ deck.draw() for i in range(6) ] #draw six cards 
        
    def __getitem__(self,i): #allows for hand[i] references to cards in hand
        return self.cards[i]
    def append(self, acards): #allows cards to be added to hand
        if type(acards) == Card: acards = [acards]
        for card in acards: #a list of cards may be passed and they will be added
            self.cards.append(card)
    def remove(self, card): #"card" may be a Card type or an int index. Card type is a bit buggy atm
        if type(card) == int:
            card = self.cards[card]
        self.cards.remove(card)
        #print(f"removed {card} from {self.name}\n",self)
    def __add__(self,other_hand): #returns a new Hand type with cards from both hands
        #print(f"debug... adding {self.name} and {other_hand.name}")
        new_hand = deepcopy(self)
        if other_hand == None: return new_hand
        for card in other_hand: new_hand.append(card)
        #print(f"adding result: {new_hand}\n... ...")
        return new_hand
    def sort(self, key = "suit"):
        cp = self.cards
        if key == "suit":
            cp = [(c.suit, c.val) for c in cp]
            cp.sort()
            cp = [ Card(s,v) for s,v in cp ]
        else:
            cp = [(c.val, c.suit) for c in cp]
            cp.sort()
            cp = [ Card(s,v) for v,s in cp ]
        self.cards = cp
        
    @property
    def n_cards(self):
        return len(self.cards)
    def __bool__(self):
        return len(self.cards) != 0
    
    
    @property
    def mat(self): #a 4xDECK_SIZE_N_VALS matrix of all cards, with a 1 in each index for each card in hand
        if self.n_cards > 1:
            mat = np.sum([card.mat for card in self], 0) #each card has a matrix and each card is unique
            # by virtue of the deck. The sum will be all zeroes and ones.
            return mat
        elif self.n_cards == 1: #one card
            mat = self[0].mat
            return mat
        else:
            return np.zeros([4,DECK_SIZE_N_VALS],int) #no cards
            
    def __str__(self): #just a way to print the hand out
        s= f"{self.name}: {self.n_cards} cards"
        for card in self:
            s += "\n\t" + str(card)
        return s
    def attack(self, possibility_mat):
        possibility_mat = np.multiply(possibility_mat,self.mat)
        possibility_vect=np.append(possibility_mat, [1]) #forfeit option...
        
        #print(possibility_vect)
        #print("DECIDING HAND", self)
        decision = self.decision_process(possibility_vect)
        if decision == DECK_SIZE: return "END"
        decision = card_i(decision)
        print("DECISION", decision)
        self.remove(decision) #play the card and take it out of hand
        return decision #either a Card type or a string "END"
        
    def defend(self, possibility_mat):
        return self.attack(possibility_mat)

    #dummy-decision process. Bare minimum algorithm. Human player version of this method
    #takes human input. A neural net would evaluate inputs and give an output...
    def decision_process(self, possibility_vect):
        #simplest possible decision... choose the first
        return list(possibility_vect).index(1) #first possible (int bc index)

class Human_Player(Hand):
    def decision_process(self, possibility_vect):
        self.sort() #convenience...
        v = possibility_vect
        print(np.sum(v[:-1]))
        if np.sum(v[:-1]) == 0:
            sleep(0.2)
            print("automatic end of turn: no further options")
            sleep(0.2)
            return DECK_SIZE
        c_list = [] #list of possible cards from hand and possibility mask
        for i, val in enumerate(v[:-1]): #ignore DECK_SIZE "FORFEIT"
            if val: c_list.append(card_i(i)) # if card is possible, get the corresponding Card object
        c_dict = {} #dictionary of possible inputs vs return values (ints)
        print("\tYOUR HAND:")
        i = 0
        for card in self: #for card in hand
            if card in c_list: #if card is a possibility
                nstr = f"({i})" #give it a number
                c_dict[i] = i_card(card) #get the Card() -> int association
                i += 1 
            else: nstr = ' • '
            print(f"\t{nstr}\t{card}")
        print(f"\t({i})\tEND TURN / FORFEIT")
        c_dict[i] = DECK_SIZE #don't forget the forfeit option!
        return c_dict[int(input("INPUT OPTION #: "))]
        
    def decision_process_old(self, possibility_vect):
        print(self)
        v = possibility_vect
        for i, val in enumerate(v):
            if i == DECK_SIZE:
                print("DECK_SIZE: FORFEIT")
                break
            if val:
                print(f"{i}: {card_i(i)}") #show the option
        return int(input("INPUT: ")) #return an int which will be passed to card_i or will be DECK_SIZE = "END"
        
        
class Deck(Hand):
    def __init__(self):
        self.cards = [ Card(s,v) for s in range(4) for v in range(DECK_SIZE_N_VALS) ]
        shuffle(self.cards)
        self.name = "DECK"
    def draw(self): #take from the top
        return self.cards.pop()

class Round:
    def __init__(self, attacker, defender, trump_suit):
        #make Hands for everything
        self.a = attacker #Hand type
        self.d = defender #Hand type
        self.open_attacks = Hand(name="OPEN ATTACKS")
        self.discard_pile = Hand(name="DISCARD PILE")
        self.trump_suit = trump_suit

        #who's who for easier readouts
        self.a.name = "ATTACKER HAND"
        self.d.name = "DEFENDER HAND"
        
        print("\n\n\t\t\tROUND START")#,self.a, "\n", self.d)
        
    def start(self):
        sleep(0.2)
        while True: #until return 
            print("\t\t\tATTACKING")
            self.do_attack()
            sleep(0.2)
            
            if self.open_attacks.n_cards == 0: #if no cards are played that implies a forfeit
                return self.hands, "ATTACK FORFEIT"
            
            print("\t\t\tDEFENDING")
            
            while self.open_attacks.n_cards > 0: #while there are open attacks...
                print(self.open_attacks)
                sleep(0.2)
                if self.do_defend() == "DEFENCE FORFEIT": #pick up the cards!
                    self.d = self.d + self.open_attacks
                    self.d = self.d + self.discard_pile
                    #print(f"debug... END OF ROUND before return...\n{self.a}\n{self.d}\n ...") 
                    return self.hands, "DEFENCE FORFEIT"
            #if somebody is out of cards, nobody loses. Effectively identical to Attack Forfeit
            if self.a.n_cards == 0 or self.d.n_cards == 0: return self.hands, "ATTACK FORFEIT"
            
    #quick way to get hands
    @property
    def hands(self):
        return self.a, self.d

    
    def do_attack(self):
        #limit cards played according to size of other guy's hand
        while self.d.n_cards > self.open_attacks.n_cards and bool(self.a): #play as many cards as you wish...
            sleep(0.2)
            #get attacker's choice. Pass the constraints from the round information
            a_card = self.a.attack(self.attack_possibilities_mat())
            if type(a_card) == Card: #if a card is played, put it into the attacks section
                self.open_attacks.append(a_card)
                if type(self.a) == Human_Player: print(self.open_attacks)
            else: return "DONE" #go until attacker returns a "forfeit"
        if self.a: return "DONE" #if attacker still has cards, all is well
        else: return "OUT" #if attacker is out of cards, take note
    def do_defend(self):
        sleep(0.2)
        #get defender's choice. Pass the constraints from the round information
        d_card = self.d.defend(self.defence_possibilities_mat()) 
        if type(d_card) == str: #if it's not a card, it's a forfeit
            return "DEFENCE FORFEIT"
        else: #move stuff to discard pile out of attack pile
            self.discard_pile.append([d_card, self.open_attacks[0]])
            self.open_attacks.remove(0)
            return "NEXT ATTACK"

    #NOTE: the possibility mats are index-by-index multiplied (not dotted, etc)
    # with the hand matrices. In this sense, they act like bitwise AND masks.
    
    def defence_possibilities_mat(self):
        card = self.open_attacks[0]
        mat = np.zeros([4,DECK_SIZE_N_VALS],int) #no options
        if card.suit != self.trump_suit:
            mat[self.trump_suit] = 1 #if the attacking card is not a trump, all trumps are better
        mat[card.suit][card.val + 1 : DECK_SIZE_N_VALS] = 1 #all cards of same suit and higher value are better
        return mat
    
    def attack_possibilities_mat(self):
        open_attacks_check = (self.open_attacks.n_cards != 0)
        discard_pile_check = (self.discard_pile.n_cards != 0)
        if open_attacks_check or discard_pile_check:
            #note: the addition would be a problem if cards are repeated.
            #They shouldn't be, since they are unique by virtue of the deck
            in_play_mat = (self.open_attacks + self.discard_pile).mat
        else: return np.ones([4,DECK_SIZE_N_VALS],int) #if no cards played, any card is good

        m = deepcopy(in_play_mat)
        #print(m)
        m = np.array( [np.sum(m.T,1), np.sum(m.T,1), np.sum(m.T,1), np.sum(m.T,1)] )
        #print(m)
        return m
        
        
        
    


class Game:
    def __init__(self):
        self.deck = Deck()
        self.trump_card = self.deck.cards[0] #bottom card is trump
        self.trump_suit = self.trump_card.suit
        global suit_str_dict
        suit_str_dict = {0: "Hearts", 1: "Diamonds", 2: "Clubs", 3: "Spades"} #reset the printout info
        suit_str_dict[self.trump_suit] += "*" #modify the printout info
        self.players = [Hand(self.deck), Human_Player(self.deck)]

        print(f"Trump Card: {self.trump_card}")

    #play a round and do a hard update on the hands.
    def do_round(self, i):

        hands, result = Round( self.players[i], self.players[1-i], self.trump_card.suit).start()
        self.players[i], self.players[1-i] = hands #hard update on hands
        sleep(0.2)
        print(result)
        sleep(0.2)
        #print out player hands... don't do this if you're playing fair
        #for player in self.players: print("END ROUND:", player)

        #draw up to 6 if the deck has cards
        while self.players[i].n_cards < 6 and bool(self.deck):
            self.players[i].append(self.deck.draw())
        while self.players[1-i].n_cards < 6 and bool(self.deck):
            self.players[1-i].append(self.deck.draw())

        # (innaccurate) win conditions...   
        if self.players[i].n_cards == 0:
            print(f"PLAYER {i} WON! \n{self.players[i]}")
            return i
        elif self.players[1-i].n_cards == 0:
            print(f"PLAYER {1-i} WON! \n{self.players[1-i]}")
            return 1-i
        if result == "DEFENCE FORFEIT": return "ROUND LOST"
        return "CONTINUE"

    def do_game(self, starting_i):
        i = starting_i
        do_round_message = self.do_round(i)
        while type(do_round_message) == str:
            if do_round_message != "ROUND LOST": i = 1 - i
            print(f"deck has {self.deck.n_cards} cards")
            do_round_message = self.do_round(i)
        if input("\n\n\t\t\tGAME OVER.\nEnter 'y' to play again!") == 'y':
            Play()
            return
        print("\n\nGoodbye!")
        sleep(2)
        
    
    
def Play():
    g = Game()
    g.do_game(randint(0,1))

    
### Actual code is only one line!
            
#Play()
