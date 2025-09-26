# The SolitaireGame engine. Deals the initial layout, enforces rules for moving cards, 
# manages passes through the stock, checks for win/loss.

from deck import Deck
from pile import Pile  # optional if Pile is in a separate file

class SolitaireGame:
    # Initialize SolitaireGame
    def __init__(self):
        # Shuffle Deck
        self.deck = Deck()
        self.deck.shuffle()

        # Add cards to all 7 tableau piles
        self.tableau = [Pile() for _ in range(7)]
        for i, pile in enumerate(self.tableau):
            cards_to_add = self.deck.draw(i + 1)
            for card in cards_to_add[:-1]:
                card.face_up = False
            cards_to_add[-1].face_up = True
            pile.add_multiple(cards_to_add)

        # Initialize foundations piles
        self.foundations = [Pile() for _ in range(4)]

        # Initialize stock pile
        self.stock = Pile(self.deck.cards)
        for card in self.stock.cards:
            card.face_up = False
        self.waste = Pile()

    # Drawing from stock pile
    def draw_from_stock(self):
        # If stock is empty
        if len(self.stock.cards) == 0:
            self.stock.cards = self.waste.cards[::-1]  # reverse waste
            for card in self.stock.cards:
                card.face_up = False
            self.waste.cards = []
        # If stock has cards
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

    def can_place_tableau(self, card, dest_pile):
        if not dest_pile.cards:  # empty pile
            return card.rank == 'king'
        top_card = dest_pile.cards[-1]
        return (
            self.is_alternate_color(card, top_card)
            and self.is_one_rank_lower(card, top_card)
        )

    def is_alternate_color(self, card1, card2):
        red = {'hearts', 'diamonds'}
        black = {'clubs', 'spades'}
        return (card1.suit in red and card2.suit in black) or \
            (card1.suit in black and card2.suit in red)

    def is_one_rank_lower(self, card1, card2):
        order = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        return order.index(card1.rank) == order.index(card2.rank) - 1
