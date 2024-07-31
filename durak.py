import numpy as np
from random import shuffle
from copy import deepcopy
card_str_dict = {0: "Hearts", 1: "Diamonds", 2: "Clubs", 3: "Spades"}

class Card:
    #suit: 0, 1, 2, 3
    def __init__(self,suit,val):
        self.suit = int(suit)
        self.val = int(val)
    @property
    def mat(self):
        mat = np.zeros([4,13],int)
        mat[self.suit][self.val] = 1
        return mat
    def __str__(self):
        return f"{self.val} of {card_str_dict[self.suit]}"
    def __eq__(self,other):
        if self.suit == other.suit and self.val == other.val: return True
        else: return False

def card_i(i): #get card by absolute value
    return Card( np.floor( i / 13), int(i%13) )

class Hand:
    def __init__(self, deck = None, name = "HAND"):
        self.name = name
        if deck == None:
            self.cards = []
            return
        self.cards = [ deck.draw() for i in range(6) ]
        
    def __getitem__(self,i):
        return self.cards[i]
    def append(self, acards):
        if type(acards) == Card: acards = [acards]
        for card in acards:
            self.cards.append(card)
    def remove(self, card):
        if type(card) == int:
            card = self.cards[card]
        self.cards.remove(card)
        #print(f"removed {card} from {self.name}\n",self)
    def __add__(self,other_hand):
        #print(f"debug... adding {self.name} and {other_hand.name}")
        new_hand = deepcopy(self)
        if other_hand == None: return new_hand
        for card in other_hand: new_hand.append(card)
        #print(f"adding result: {new_hand}\n... ...")
        return new_hand
    
    @property
    def n_cards(self):
        return len(self.cards)
    def __bool__(self):
        return len(self.cards) != 0
    
    @property
    def mat(self):
        if self.n_cards > 1:
            mat = np.sum([card.mat for card in self], 0)
            return mat
        elif self.n_cards == 1:
            mat = self[0].mat
            return mat
        else:
            return np.zeros([4,13],int)
            
    def __str__(self):
        s= f"{self.name}: {self.n_cards} cards"
        for card in self:
            s += "\n\t" + str(card)
        return s
    def attack(self, possibility_mat):
        possibility_mat = np.multiply(possibility_mat,self.mat)
        possibility_vect=np.append(possibility_mat, [1]) #forfeit option...
        
        #simplest possible decision... choose the first
        #print(possibility_vect)
        #print("DECIDING HAND", self)
        decision = self.decision_process(possibility_vect)
        if decision == 52: return "END"
        decision = card_i(decision)
        print("DECISION", decision)
        self.remove(decision) #play the card and take it out of hand
        return decision
        
    def defend(self, possibility_mat):
        return self.attack(possibility_mat)
    
    def decision_process(self, possibility_vect):
        return list(possibility_vect).index(1) #first possible (int bc index)

class Human_Player(Hand):
    def decision_process(self, possibility_vect):
        print(self)
        v = possibility_vect
        for i, val in enumerate(v):
            if i ==52:
                print("52: FORFEIT")
                break
            if val:
                print(f"{i}: {card_i(i)}")
        return int(input("INPUT: "))
        
        
class Deck(Hand):
    def __init__(self):
        self.cards = [ Card(s,v) for s in range(4) for v in range(13) ]
        shuffle(self.cards)
    def draw(self):
        return self.cards.pop()

class Round:
    def __init__(self, attacker, defender, trump_suit):
        self.a = attacker #Hand type
        self.d = defender #Hand type
        self.open_attacks = Hand(name="OPEN ATTACKS")
        self.discard_pile = Hand(name="DISCARD PILE")
        self.trump_suit = trump_suit

        self.a.name = "ATTACKER HAND"
        self.d.name = "DEFENDER HAND"
        
        print("\n\n\t\t\tROUND START")#,self.a, "\n", self.d)
        
    def start(self):
        while True:
            print("\t\t\tATTACKING")
            self.do_attack()
            
            if self.open_attacks.n_cards == 0:
                return self.hands, "ATTACK FORFEIT"
            
            print("\t\t\tDEFENDING")
            
            while self.open_attacks.n_cards > 0: #while there are open attacks...
                print(self.open_attacks)
                if self.do_defend() == "DEFENCE FORFEIT":
                    self.d = self.d + self.open_attacks
                    self.d = self.d + self.discard_pile
                    #print(f"debug... END OF ROUND before return...\n{self.a}\n{self.d}\n ...") 
                    return self.hands, "DEFENCE FORFEIT"
            if self.a.n_cards == 0 or self.d.n_cards == 0: return self.hands, "ATTACK FORFEIT"
        
    @property
    def hands(self):
        return self.a, self.d
    def do_attack(self):
        while self.d.n_cards > self.open_attacks.n_cards and bool(self.a): #play as many cards as you wish...
            a_card = self.a.attack(self.attack_possibilities_mat())
            if type(a_card) == Card:
                self.open_attacks.append(a_card)
                print(self.open_attacks)
            else: return "DONE" #go until attacker returns a zero  
        if self.a: return "DONE"
        else: return "OUT"
    def do_defend(self):   
        d_card = self.d.defend(self.defence_possibilities_mat())
        if type(d_card) == str:
            return "DEFENCE FORFEIT"
        else: #move stuff to discard pile out of attack pile
            self.discard_pile.append([d_card, self.open_attacks[0]])
            self.open_attacks.remove(0)
            return "NEXT ATTACK"
            
            
                
        
        
    def defence_possibilities_mat(self):
        card = self.open_attacks[0]
        mat = np.zeros([4,13],int) #no options
        if card.suit != self.trump_suit:
            mat[self.trump_suit] = 1 #if the attacking card is not a trump, all trumps are better
        mat[card.suit][card.val + 1 : 13] = 1 #all cards of same suit and higher value are better
        return mat
    
    def attack_possibilities_mat(self):
        open_attacks_check = (self.open_attacks.n_cards != 0)
        discard_pile_check = (self.discard_pile.n_cards != 0)
        if open_attacks_check or discard_pile_check:
            #note: the addition would be a problem if cards are repeated.
            #They shouldn't be, since they are unique by virtue of the deck
            in_play_mat = (self.open_attacks + self.discard_pile).mat
        #elif open_attacks_check:
        #    print(self.open_attacks)
        #    in_play_mat = self.open_attacks.mat
        #elif discard_pile_check:
        #    in_play_mat = self.discard_pile.mat
        else: return np.ones([4,13],int) #if no cards played, any card is good

        m = deepcopy(in_play_mat)
        #print(m)
        m = np.array( [np.sum(m.T,1), np.sum(m.T,1), np.sum(m.T,1), np.sum(m.T,1)] )
        #print(m)
        return m
        
        
        
    


class Game:
    def __init__(self):
        self.deck = Deck()
        self.trump_card = self.deck.cards[0]
        self.trump_suit = self.trump_card.suit
        global card_str_dict
        card_str_dict[self.trump_suit] += "*"
        self.players = [Hand(self.deck), Human_Player(self.deck)]

        print(f"Trump Card: {self.trump_card}")
    def do_round(self, i):

        hands, result =Round( self.players[i], self.players[1-i], self.trump_card.suit).start()
        self.players[i], self.players[1-i] = hands

        #print(result)
        for player in self.players: print("END ROUND:", player)
        
        while self.players[i].n_cards < 6 and bool(self.deck):
            self.players[i].append(self.deck.draw())
        while self.players[1-i].n_cards < 6 and bool(self.deck):
            self.players[1-i].append(self.deck.draw())
            
        if self.players[i].n_cards == 0:
            print(f"PLAYER {i} WON! \n{self.players[i]}")
            return str(i)
        elif self.players[1-i].n_cards == 0:
            print(f"PLAYER {1-i} WON! \n{self.players[1-i]}")
            return str(1-i)
        if result == "DEFENCE FORFEIT": return "ROUND LOST"
        return "CONTINUE"

    def do_game(self, starting_i):
        i = starting_i
        do_round_message = self.do_round(i)
        while type(do_round_message) == str:
            if do_round_message != "ROUND LOST": i = 1 - i
            print(f"deck has {self.deck.n_cards} cards")
            do_round_message = self.do_round(i)
    
    


g = Game()
for player in g.players: print(player)

g.do_game(0)
