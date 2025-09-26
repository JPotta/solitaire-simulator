
# Holds the Deck class → creates 52 Card objects, shuffles, 
# or sets up a special test order. Exposes draw() to pull cards.

import random
from card import Card

class Deck:
    # Initialize Deck
    def __init__(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]
        self.shuffle()

    # Shuffle Cards according to algorithm assigned
    def shuffle(self):
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    # Reset cards for new game
    def reset(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        self.cards = [Card(rank, suit) for suit in suits for rank in ranks]

    # Draw next card
    def draw(self, n=1):
        drawn_cards = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn_cards


