# Defines pile types:

# Tableau (7 columns, alternating colors, descending rank).

# Foundation (4 suit piles, Ace → King).
# Stock & Waste (cards drawn and recycled).

class Pile:
    def __init__(self, cards=None):
        self.cards = cards if cards else []
    
    def add(self, card):
        self.cards.append(card)

    def add_multiple(self, cards):
        self.cards.extend(cards)

    def draw(self, n=1):
        drawn = self.cards[:n]
        self.cards = self.cards[n:]
        return drawn
    
    def peek(self):
        return self.cards[-1] if self.cards else None

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return f"Pile({self.cards})"