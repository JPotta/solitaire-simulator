# Defines pile types:

# Tableau (7 columns, alternating colors, descending rank).

# Foundation (4 suit piles, Ace → King).
# Stock & Waste (cards drawn and recycled).

class Pile:
    """
    Represents a pile of cards in the game.
    """
    def __init__(self, cards=None):
        """
        Initializes a Pile object.

        Args:
            cards (list, optional): A list of Card objects to initialize the pile.
        """
        self.cards = cards if cards else []
    
    def add(self, card):
        """
        Adds a single card to the top of the pile.
        """
        self.cards.append(card)

    def add_multiple(self, cards):
        """
        Adds a list of cards to the top of the pile.
        """
        self.cards.extend(cards)

    def draw(self, n=1):
        """
        Draws n cards from the top of the pile and removes them.

        Args:
            n (int): The number of cards to draw.

        Returns:
            list: A list of the drawn Card objects.
        """
        if n > len(self.cards):
            n = len(self.cards) # Don't try to draw more cards than exist
        drawn = self.cards[-n:]
        self.cards = self.cards[:-n]
        return drawn
    
    def peek(self):
        """
        Looks at the top card of the pile without removing it.

        Returns:
            Card: The top Card object, or None if the pile is empty.
        """
        return self.cards[-1] if self.cards else None

    def __len__(self):
        """
        Returns the number of cards in the pile.
        """
        return len(self.cards)

    def __repr__(self):
        """
        Provides a string representation of the pile.
        """
        return f"Pile({self.cards})"
