# Holds the Deck class → creates 52 Card objects, shuffles, 
# or sets up a special test order. Exposes draw() to pull cards.

import random
from card import Card

class Deck:
    """
    Represents a deck of 52 playing cards.
    """
    def __init__(self):
        """
        Initializes a Deck object, creating and shuffling 52 cards.
        """
        # These need to be attributes of the instance to be accessed from outside
        self.suits = ['hearts', 'diamonds', 'clubs', 'spades']
        self.ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]
        self.shuffle()

    def shuffle(self):
        """
        Shuffles the deck using the Fisher-Yates (Knuth version) algorithm.
        """
        n = len(self.cards)
        for i in range(n - 1, 0, -1):
            j = random.randint(0, i)
            self.cards[i], self.cards[j] = self.cards[j], self.cards[i]

    def reset(self):
        """
        Resets the deck to its initial, unshuffled state.
        """
        self.cards = [Card(rank, suit) for suit in self.suits for rank in self.ranks]

    def draw(self, n=1):
        """
        Draws n cards from the top of the deck.

        Args:
            n (int): The number of cards to draw.

        Returns:
            list: A list of the drawn Card objects.
        """
        drawn_cards = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn_cards
