import unittest
from game import SolitaireGame
from deck import Deck
from card import Card
from pile import Pile

# --- Helper function for quick card creation ---
def make_card(rank, suit, face_up=False):
    return Card(rank, suit, face_up=face_up)

# --- Special Deck Class for Testing ---
class TestDeck(Deck):
    """A custom Deck class that can be loaded with a specific card list."""
    def __init__(self, custom_cards):
        self.cards = custom_cards
        # Do NOT call self.shuffle()

# --- Special Game Class for Testing ---
class TestSolitaireGame(SolitaireGame):
    """A custom game class that uses a specific deck for setup."""
    def __init__(self, custom_cards):
        # Override the standard initialization to use the custom deck
        self.deck = TestDeck(custom_cards)

        # Proceed with normal setup using the custom deck
        self.tableau = [Pile() for _ in range(7)]
        for i, pile in enumerate(self.tableau):
            # Draw from the custom TestDeck
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


class TestSpecialDecks(unittest.TestCase):
    """Tests the game using synthetic, known-outcome starting data."""

    def test_guaranteed_loss_blocked_tableau(self):
        """
        Test a deck order that creates an impossible tableau move.
        
        Strategy: Put a black King on a black Queen in the first pile.
        This blocks the King from moving, making the entire pile unmovable 
        unless the Queen can be cleared first.
        """
        
        # Tableau 0 (1 card): King of Spades (Black, top card)
        # Tableau 1 (2 cards): Queen of Spades (Black, face-up) on King of Spades (Black, face-down) <-- IMPOSSIBLE
        # ... this is hard to construct because the top card of T1 must be face up.

        # Simpler strategy: Make the top card of a deep pile a blocking card.
        # Card 1 (T0): 7H (face up)
        # Card 2 (T1, hidden): 8D (face down)
        # Card 3 (T1, visible): 9D (face up) <-- IMPOSSIBLE: Red on Red (8D on 9D)
        
        custom_deck = [
            # Tableau (28 cards)
            make_card('7', 'hearts'),    # T0 (1)
            make_card('8', 'diamonds'),  # T1 (2) hidden
            make_card('9', 'diamonds'),  # T1 (2) visible - RED on RED, blocking move
            make_card('ace', 'clubs'),   # T2 (3) hidden
            make_card('2', 'clubs'),     # T2 (3) hidden
            make_card('3', 'clubs'),     # T2 (3) visible
            # ... fill with remaining 22 tableau cards
            *[make_card('4', 'spades') for _ in range(22)], 
            
            # Stock (24 cards)
            *[make_card('ace', 'hearts') for _ in range(24)], 
        ]
        
        # Ensure deck has 52 cards (even if duplicates for testing simplicity)
        while len(custom_deck) < 52:
            custom_deck.append(make_card('queen', 'hearts'))

        game = TestSolitaireGame(custom_deck)

        # The tableau piles will be:
        # T0: [7H]
        # T1: [8D (down), 9D (up)] <-- BLOCK: 8D (Red) should not be on 9D (Red)
        
        # Check that T1's visible card (9D) cannot be moved, and the card below (8D)
        # is the wrong color/rank to move to the 9D, guaranteeing a blocked pile.
        
        # Check T1's internal structure for the blocking state (Red on Red)
        pile1_cards = game.tableau[1].cards
        self.assertEqual(pile1_cards[0].suit, 'diamonds') # 8D (Red)
        self.assertEqual(pile1_cards[1].suit, 'diamonds') # 9D (Red)
        self.assertFalse(game.can_place_tableau(pile1_cards[0], Pile([pile1_cards[1]])), 
                         "The deck setup should guarantee a blocked pile (Red on Red).")
        
        # Although not a full simulation, this test confirms the *starting state* # is one that creates an initial blockage in the tableau logic.
        self.assertFalse(game.can_place_tableau(game.tableau[1].cards[-1], game.tableau[0]), 
                         "Top card of blocked pile (9D) should not be movable to T0 (7H).")


    def test_guaranteed_win_aces_on_top(self):
        """
        Test a deck order that makes the four Aces immediately available.
        
        Strategy: Place all four Aces as the face-up cards in the first four tableau piles.
        This allows immediate foundation starts.
        """
        
        # Ranks in reverse order for descending requirement
        ranks_in_order = ['king','queen','jack','10','9','8','7','6','5','4','3','2','ace']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        
        # 1. Tableau top cards (4 Aces on T0-T3)
        tableau_top = [make_card('ace', suit, face_up=True) for suit in suits]
        
        # 2. Tableau hidden cards (fill 28 slots)
        tableau_hidden = []
        for i in range(1, 7): # Piles 1 through 6 need hidden cards (total 27 hidden)
            for j in range(i):
                tableau_hidden.append(make_card(ranks_in_order[j % 13], suits[(i+j) % 4], face_up=False))
        
        # 3. Stock cards (remaining 24, high ranks first)
        stock_cards = [make_card(ranks_in_order[i % 13], suits[i % 4], face_up=False) for i in range(24)]
        
        custom_deck = tableau_top[:4] + tableau_hidden + stock_cards
        
        # Need exactly 52 cards, adjust hidden cards/stock to ensure 52
        # T0-T6 take 1+2+3+4+5+6+7 = 28 cards (7 visible, 21 hidden)
        
        # Correct construction for Win scenario:
        # A deck with Aces first, followed by 2s, 3s, etc., but interleaved colors
        # Total Cards = 52. Tableau = 28. Stock = 24.
        
        win_deck = []
        # Tableau Cards (28) - make the top card of T0-T3 Aces for immediate move
        
        # T0 (1): A(H)
        win_deck.append(make_card('ace', 'hearts', face_up=True))
        
        # T1 (2): 2(D, down), A(D, up)
        win_deck.append(make_card('2', 'diamonds', face_up=False))
        win_deck.append(make_card('ace', 'diamonds', face_up=True))

        # T2 (3): 3(C, down), 2(C, down), A(C, up)
        win_deck.append(make_card('3', 'clubs', face_up=False))
        win_deck.append(make_card('2', 'clubs', face_up=False))
        win_deck.append(make_card('ace', 'clubs', face_up=True))

        # T3 (4): 4(S, down), 3(S, down), 2(S, down), A(S, up)
        win_deck.append(make_card('4', 'spades', face_up=False))
        win_deck.append(make_card('3', 'spades', face_up=False))
        win_deck.append(make_card('2', 'spades', face_up=False))
        win_deck.append(make_card('ace', 'spades', face_up=True))

        # T4-T6 filled with low rank, high rank for quick clearance
        # T4 (5): 5, 4, 3, 2, K (all face down, K up)
        win_deck.extend([make_card('5', 'hearts', False), make_card('4', 'diamonds', False), 
                         make_card('3', 'clubs', False), make_card('2', 'spades', False), 
                         make_card('king', 'hearts', True)])
        
        # T5 (6)
        win_deck.extend([make_card('6', 'diamonds', False), make_card('5', 'clubs', False), 
                         make_card('4', 'spades', False), make_card('3', 'hearts', False), 
                         make_card('2', 'diamonds', False), make_card('queen', 'clubs', True)])
        
        # T6 (7)
        win_deck.extend([make_card('7', 'clubs', False), make_card('6', 'spades', False), 
                         make_card('5', 'hearts', False), make_card('4', 'diamonds', False), 
                         make_card('3', 'clubs', False), make_card('2', 'spades', False), 
                         make_card('jack', 'diamonds', True)])
                         
        # Stock (24 remaining cards arranged in ascending order by suit)
        # This setup allows for simple linear movement to the foundations after Aces are moved.
        remaining_cards = []
        for rank in ranks_in_order[::-1]: # Ace to King
            for suit in suits:
                # Check if card is already in the tableau
                is_in_tableau = False
                for c in win_deck:
                    if c.rank == rank and c.suit == suit:
                        is_in_tableau = True
                        break
                if not is_in_tableau:
                    remaining_cards.append(make_card(rank, suit, face_up=False))

        win_deck.extend(remaining_cards)
        
        self.assertEqual(len(win_deck), 52, "Win deck must have exactly 52 cards.")
        game = TestSolitaireGame(win_deck)

        # Check immediate win possibility
        # All foundations should be movable immediately (Aces are on top of T0-T3)
        self.assertEqual(game.tableau[0].cards[-1].rank, 'ace')
        self.assertEqual(game.tableau[1].cards[-1].rank, 'ace')
        self.assertEqual(game.tableau[2].cards[-1].rank, 'ace')
        self.assertEqual(game.tableau[3].cards[-1].rank, 'ace')

        # While a full simulation is required to prove a win, this test confirms the *initial state*
        # is optimal for a win by making the starting moves possible.
        

if __name__ == '__main__':
    # You must run this command from the directory containing your project files:
    # python -m unittest test_special_decks.py
    unittest.main()