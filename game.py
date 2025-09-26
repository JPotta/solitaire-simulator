# The SolitaireGame engine. Deals the initial layout, enforces rules for moving cards, 
# manages passes through the stock, checks for win/loss.

from deck import Deck
from pile import Pile  # optional if Pile is in a separate file

class SolitaireGame:
    def __init__(self):
        self.deck = Deck()
        self.deck.shuffle()

        self.tableau = [Pile() for _ in range(7)]
        for i, pile in enumerate(self.tableau):
            cards_to_add = self.deck.draw(i + 1)
            for card in cards_to_add[:-1]:
                card.face_up = False
            cards_to_add[-1].face_up = True
            pile.add_multiple(cards_to_add)

        self.foundations = [Pile() for _ in range(4)]

        self.stock = Pile(self.deck.cards)
        for card in self.stock.cards:
            card.face_up = False
        self.waste = Pile()

    def draw_from_stock(self):
        if len(self.stock.cards) == 0:
            self.stock.cards = self.waste.cards[::-1]  # reverse waste
            for card in self.stock.cards:
                card.face_up = False
            self.waste.cards = []
        else:
            card = self.stock.draw()[0]
            card.flip()
            self.waste.add(card)

    def move_tableau_to_tableau(self, src_index, dest_index, num_cards):
        moving_cards = self.tableau[src_index].draw(num_cards)
        self.tableau[dest_index].add_multiple(moving_cards)

    def move_tableau_to_foundation(self, tableau_index, foundation_index):
        card = self.tableau[tableau_index].draw()[0]
        self.foundations[foundation_index].add(card)

    def move_waste_to_tableau(self, tableau_index):
        if len(self.waste.cards) > 0:
            card = self.waste.draw()[0]
            self.tableau[tableau_index].add(card)

    def move_waste_to_foundation(self, foundation_index):
        if len(self.waste.cards) > 0:
            card = self.waste.draw()[0]
            self.foundations[foundation_index].add(card)

    def is_won(self):
        return all(len(f.cards) == 13 for f in self.foundations)
