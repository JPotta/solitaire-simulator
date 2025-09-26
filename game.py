# The SolitaireGame engine. Deals the initial layout, enforces rules for moving cards, 
# manages passes through the stock, checks for win/loss.

from deck import Deck
from pile import Pile
from card import Card

class SolitaireGame:
    """
    Manages the state and rules of a game of Solitaire.
    """
    def __init__(self, shuffled_cards=None):
        """
        Initializes a SolitaireGame.

        Args:
            shuffled_cards (list, optional): A list of cards to use for the game
                                             instead of a randomly shuffled deck.
                                             Useful for testing.
        """
        self.deck = Deck()
        if shuffled_cards:
            self.deck.cards = shuffled_cards

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

        self.passes_through_stock = 0
        self.max_passes = 3

    def can_move_tableau_to_tableau(self, src_index, dest_index, num_cards):
        """
        Checks if a move from one tableau pile to another is valid.
        """
        if num_cards > len(self.tableau[src_index].cards):
            return False
        
        moving_cards = self.tableau[src_index].cards[-num_cards:]
        if not all(card.face_up for card in moving_cards):
            return False

        last_card = moving_cards[0]
        
        if len(self.tableau[dest_index].cards) == 0:
            return last_card.rank == 'king'
        
        top_card_dest = self.tableau[dest_index].peek()
        return (last_card.get_color() != top_card_dest.get_color() and
                last_card.get_value() == top_card_dest.get_value() - 1)

    def move_tableau_to_tableau(self, src_index, dest_index, num_cards):
        """
        Moves a stack of cards from one tableau pile to another.
        """
        if self.can_move_tableau_to_tableau(src_index, dest_index, num_cards):
            moving_cards = self.tableau[src_index].draw(num_cards)
            self.tableau[dest_index].add_multiple(moving_cards)
            # Flip the new top card of the source pile if it's face down
            if self.tableau[src_index].cards and not self.tableau[src_index].peek().face_up:
                self.tableau[src_index].peek().flip()
            return True
        return False
        
    def can_move_tableau_to_foundation(self, tableau_index):
        """
        Checks if a move from a tableau pile to a foundation is valid.
        """
        if not self.tableau[tableau_index].cards:
            return False
        card_to_move = self.tableau[tableau_index].peek()
        
        for foundation in self.foundations:
            if not foundation.cards and card_to_move.rank == 'ace':
                return True
            if foundation.cards:
                top_card_foundation = foundation.peek()
                if (top_card_foundation.suit == card_to_move.suit and
                    top_card_foundation.get_value() == card_to_move.get_value() - 1):
                    return True
        return False

    def move_tableau_to_foundation(self, tableau_index):
        """
        Moves the top card of a tableau pile to the correct foundation.
        """
        if self.can_move_tableau_to_foundation(tableau_index):
            card_to_move = self.tableau[tableau_index].peek()
            
            for foundation in self.foundations:
                if not foundation.cards and card_to_move.rank == 'ace':
                    card = self.tableau[tableau_index].draw()[0]
                    foundation.add(card)
                    # Flip the new top card of the tableau pile
                    if self.tableau[tableau_index].cards and not self.tableau[tableau_index].peek().face_up:
                        self.tableau[tableau_index].peek().flip()
                    return True
                if foundation.cards:
                    top_card_foundation = foundation.peek()
                    if (top_card_foundation.suit == card_to_move.suit and
                        top_card_foundation.get_value() == card_to_move.get_value() - 1):
                        card = self.tableau[tableau_index].draw()[0]
                        foundation.add(card)
                        # Flip the new top card of the tableau pile
                        if self.tableau[tableau_index].cards and not self.tableau[tableau_index].peek().face_up:
                            self.tableau[tableau_index].peek().flip()
                        return True
        return False

    def can_move_waste_to_tableau(self, tableau_index):
        """
        Checks if a move from the waste pile to a tableau is valid.
        """
        if not self.waste.cards:
            return False
        card_to_move = self.waste.peek()
        
        if not self.tableau[tableau_index].cards:
            return card_to_move.rank == 'king'
            
        top_card_tableau = self.tableau[tableau_index].peek()
        return (card_to_move.get_color() != top_card_tableau.get_color() and
                card_to_move.get_value() == top_card_tableau.get_value() - 1)
        
    def move_waste_to_tableau(self, tableau_index):
        """
        Moves the top card of the waste pile to a tableau.
        """
        if self.can_move_waste_to_tableau(tableau_index):
            card = self.waste.draw()[0]
            self.tableau[tableau_index].add(card)
            return True
        return False

    def can_move_waste_to_foundation(self):
        """
        Checks if a move from the waste pile to a foundation is valid.
        """
        if not self.waste.cards:
            return False
        card_to_move = self.waste.peek()
        
        for foundation in self.foundations:
            if not foundation.cards and card_to_move.rank == 'ace':
                return True
            if foundation.cards:
                top_card_foundation = foundation.peek()
                if (top_card_foundation.suit == card_to_move.suit and
                    top_card_foundation.get_value() == card_to_move.get_value() - 1):
                    return True
        return False

    def move_waste_to_foundation(self):
        """
        Moves the top card of the waste pile to the correct foundation.
        """
        if self.can_move_waste_to_foundation():
            card_to_move = self.waste.peek()
            
            for foundation in self.foundations:
                if not foundation.cards and card_to_move.rank == 'ace':
                    card = self.waste.draw()[0]
                    foundation.add(card)
                    return True
                if foundation.cards:
                    top_card_foundation = foundation.peek()
                    if (top_card_foundation.suit == card_to_move.suit and
                        top_card_foundation.get_value() == card_to_move.get_value() - 1):
                        card = self.waste.draw()[0]
                        foundation.add(card)
                        return True
        return False

    def draw_from_stock(self):
        """
        Draws one card from the stock to the waste pile. If the stock is empty,
        it recycles the waste pile to the stock.
        """
        if len(self.stock.cards) == 0:
            if self.passes_through_stock >= self.max_passes:
                return False # Cannot draw from stock anymore
            self.stock.cards = self.waste.cards[::-1]  # reverse waste
            for card in self.stock.cards:
                card.face_up = False
            self.waste.cards = []
            self.passes_through_stock += 1
            return True
        else:
            card = self.stock.draw()[0]
            card.flip()
            self.waste.add(card)
            return True
            
    def is_won(self):
        """
        Checks if the game has been won.
        """
        return all(len(f.cards) == 13 for f in self.foundations)

    def is_lost(self):
        """
        Checks if the game is in an unwinnable state.
        This is a simplified check for the simulation.
        """
        # If there are no possible moves
        # A simple check: if we've gone through the stock too many times
        return self.passes_through_stock >= self.max_passes and len(self.stock.cards) == 0 and not self.has_possible_moves()

    def has_possible_moves(self):
        """
        Checks if any valid moves are available.
        (This is a simplified check for the simulation, a real AI would need a more complex
        move-finding algorithm.)
        """
        # Check waste to tableau/foundation
        if self.can_move_waste_to_foundation() or any(self.can_move_waste_to_tableau(i) for i in range(7)):
            return True
        
        # Check tableau to foundation
        if any(self.can_move_tableau_to_foundation(i) for i in range(7)):
            return True
        
        # Check tableau to tableau
        for i in range(7):
            if not self.tableau[i].cards or not self.tableau[i].peek().face_up:
                continue
            for j in range(7):
                if i != j and self.can_move_tableau_to_tableau(i, j, 1):
                    return True
        return False
