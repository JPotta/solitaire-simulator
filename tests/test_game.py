import unittest
import random
from game import SolitaireGame
from pile import Pile
from card import Card

def make_card(rank, suit, face_up=False):
    """Utility to quickly create a Card object."""
    return Card(rank, suit, face_up=face_up)

class TestSolitaireGame(unittest.TestCase):
    """Tests for the main SolitaireGame logic."""

    def setUp(self):
        """Initialize a fresh game for each test. Use a fixed seed for consistency."""
        random.seed(42) 
        self.game = SolitaireGame()

    def test_initial_setup(self):
        """Test that the game is set up correctly (28 tableau, 24 stock)."""
        
        total_tableau_cards = 0
        for i, pile in enumerate(self.game.tableau):
            self.assertEqual(len(pile.cards), i + 1)
            self.assertTrue(pile.cards[-1].face_up)
            total_tableau_cards += len(pile.cards)
            
        self.assertEqual(total_tableau_cards, 28)
        self.assertEqual(len(self.game.stock.cards), 24)
        self.assertEqual(len(self.game.waste.cards), 0)

    def test_draw_from_stock_and_recycle(self):
        """Test drawing one card at a time and recycling the waste."""
        
        initial_stock_len = len(self.game.stock.cards) # 24
        
        # Draw one card
        self.game.draw_from_stock()
        self.assertEqual(len(self.game.stock.cards), 23)
        self.assertEqual(len(self.game.waste.cards), 1)
        
        # Exhaust the stock (draw remaining 23)
        for _ in range(23):
            self.game.draw_from_stock()
        self.assertEqual(len(self.game.stock.cards), 0)
        self.assertEqual(len(self.game.waste.cards), 24)
        
        # Recycle the waste (draw again)
        self.game.draw_from_stock() 
        self.assertEqual(len(self.game.stock.cards), 23) # Stock is reset (24-1)
        self.assertEqual(len(self.game.waste.cards), 1)

    def test_can_place_tableau_rules(self):
        """Test alternating color and descending rank rule for tableau placement."""
        
        # Valid: Red Queen ('hearts') on Black King ('spades')
        red_queen = make_card('queen', 'hearts')
        black_king_pile = Pile([make_card('king', 'spades')])
        self.assertTrue(self.game.can_place_tableau(red_queen, black_king_pile))
        
        # Invalid: Same color (Red Queen on Red King)
        red_king_pile = Pile([make_card('king', 'diamonds')])
        self.assertFalse(self.game.can_place_tableau(red_queen, red_king_pile))

    def test_is_won(self):
        """Test the win condition (all foundations full)."""
        self.assertFalse(self.game.is_won())
        
        # Populate all foundations with 13 cards (Ace to King)
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        
        for i, f in enumerate(self.game.foundations):
            suit = suits[i]
            for rank in ranks:
                f.add(make_card(rank, suit))
                
        self.assertTrue(self.game.is_won())


if __name__ == '__main__':
    unittest.main()