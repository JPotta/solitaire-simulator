# Defines pile types:

# Tableau (7 columns, alternating colors, descending rank).

# Foundation (4 suit piles, Ace → King).
# Stock & Waste (cards drawn and recycled).

class Pile:
    # Initialize Pile
    def __init__(self, cards=None):
        self.cards = cards if cards else []
    
    # Add card to pile
    def add(self, card):
        self.cards.append(card)

    # Add multiple cards to pile
    def add_multiple(self, cards):
        self.cards.extend(cards)

    # Draw card from pile
    def draw(self, n=1):
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn
    
    # Peek at next card
    def peek(self):
        return self.cards[-1] if self.cards else None

    # Length of pile
    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Pile({self.cards})"