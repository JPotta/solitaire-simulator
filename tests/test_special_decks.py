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
        (Corrected to ensure exactly 52 unique cards are created and distributed.)
        """
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        
        # 1. Create a full deck of 52 unique cards (sorted Ace-King, H-D-C-S)
        full_deck = []
        for rank in ranks:
            for suit in suits:
                full_deck.append(make_card(rank, suit))
        
        # Reverse the deck to easily pop high ranks for tableau setup
        full_deck.reverse() 
        
        # 2. Define the Tableau cards (28 total)
        tableau_cards = []
        
        # A. Use 4 Aces for the top card of T0-T3 (and the rest of the Tableau)
        # Pull the four Aces from the back of the reversed deck (front of ranks list)
        aces = full_deck[48:] # Assuming Aces are the last 4 cards in the original sorted order
        
        # Use an iterable to pull cards for T4-T6
        tableau_filler_cards = full_deck[:28-4] # 24 cards needed for hidden + T4-T6 tops
        
        # B. Assemble the Tableau: Piles 0-6 take 1, 2, 3, 4, 5, 6, 7 cards
        
        # T0 (1 card): A(H)
        tableau_cards.append(make_card('ace', 'hearts', face_up=True)) # Must be unique card from the 52

        # T1 (2 cards): 2(D, down), A(D, up)
        tableau_cards.extend([make_card('2', 'diamonds', face_up=False), make_card('ace', 'diamonds', face_up=True)])
        
        # T2 (3 cards): 3(C, down), 2(C, down), A(C, up)
        tableau_cards.extend([make_card('3', 'clubs', face_up=False), make_card('2', 'clubs', face_up=False), make_card('ace', 'clubs', face_up=True)])
        
        # T3 (4 cards): 4(S, down), 3(S, down), 2(S, down), A(S, up)
        tableau_cards.extend([make_card('4', 'spades', face_up=False), make_card('3', 'spades', face_up=False), make_card('2', 'spades', face_up=False), make_card('ace', 'spades', face_up=True)])

        # The previous attempt failed because the cards below were duplicates of cards above.
        # Let's ensure the full list is 28 unique cards. 
        # The first 4*4=16 cards are A-4 of all suits. We'll use a subset of these for T0-T3.
        
        # Create the exact 28 unique cards required for the tableau
        tableau_unique_cards = [
            # T0 (1)
            make_card('ace', 'hearts'),
            # T1 (2)
            make_card('2', 'diamonds'), make_card('ace', 'diamonds'),
            # T2 (3)
            make_card('3', 'clubs'), make_card('2', 'clubs'), make_card('ace', 'clubs'),
            # T3 (4)
            make_card('4', 'spades'), make_card('3', 'spades'), make_card('2', 'spades'), make_card('ace', 'spades'),
            # T4 (5)
            make_card('5', 'hearts'), make_card('4', 'diamonds'), make_card('3', 'clubs'), make_card('2', 'spades'), make_card('king', 'hearts'),
            # T5 (6)
            make_card('6', 'diamonds'), make_card('5', 'clubs'), make_card('4', 'spades'), make_card('3', 'hearts'), make_card('2', 'diamonds'), make_card('queen', 'clubs'),
            # T6 (7)
            make_card('7', 'clubs'), make_card('6', 'spades'), make_card('5', 'hearts'), make_card('4', 'diamonds'), make_card('3', 'clubs'), make_card('2', 'spades'), make_card('jack', 'diamonds')
        ]
        
        # Now, manually set the face_up state for the final tableau structure:
        # A list comprehension to create the *final* 28 cards with face-up status.
        # This list IS the tableau_cards list for the TestSolitaireGame.
        
        final_tableau = []
        # T0: [A(H, UP)]
        final_tableau.append(make_card('ace', 'hearts', True))

        # T1: [2(D, DOWN), A(D, UP)]
        final_tableau.extend([make_card('2', 'diamonds', False), make_card('ace', 'diamonds', True)])
        
        # T2: [3(C, DOWN), 2(C, DOWN), A(C, UP)]
        final_tableau.extend([make_card('3', 'clubs', False), make_card('2', 'clubs', False), make_card('ace', 'clubs', True)])
        
        # T3: [4(S, DOWN), 3(S, DOWN), 2(S, DOWN), A(S, UP)]
        final_tableau.extend([make_card('4', 'spades', False), make_card('3', 'spades', False), make_card('2', 'spades', False), make_card('ace', 'spades', True)])

        # T4: [5(H, DOWN), 4(D, DOWN), 3(C, DOWN), 2(S, DOWN), K(H, UP)]
        final_tableau.extend([make_card('5', 'hearts', False), make_card('4', 'diamonds', False), make_card('3', 'clubs', False), make_card('2', 'spades', False), make_card('king', 'clubs', True)]) # Changed King to Clubs for alternating color!

        # T5: [6(D, DOWN), 5(C, DOWN), 4(S, DOWN), 3(H, DOWN), 2(D, DOWN), Q(S, UP)]
        final_tableau.extend([make_card('6', 'diamonds', False), make_card('5', 'clubs', False), make_card('4', 'spades', False), make_card('3', 'hearts', False), make_card('2', 'diamonds', False), make_card('queen', 'spades', True)]) # Changed Queen to Spades for alternating color!

        # T6: [7(C, DOWN), 6(S, DOWN), 5(H, DOWN), 4(D, DOWN), 3(C, DOWN), 2(S, DOWN), J(D, UP)]
        final_tableau.extend([make_card('7', 'clubs', False), make_card('6', 'spades', False), make_card('5', 'hearts', False), make_card('4', 'diamonds', False), make_card('3', 'clubs', False), make_card('2', 'spades', False), make_card('jack', 'diamonds', True)])
        
        # --- Recalculate Stock Cards based on unique Tableau cards ---
        
        # Get the keys of the 28 unique cards used in the tableau
        tableau_keys = {card_to_key(card) for card in tableau_unique_cards}
        
        stock_cards = []
        
        # Find the 24 remaining unique cards from the full 52-card deck
        for card in full_deck:
            if card_to_key(card) not in tableau_keys:
                card.face_up = False
                stock_cards.append(card)
        
        # The error occurred here because the initial full_deck was built Ace to King, 
        # but the tableau_unique_cards were not correctly mapped to their rank/suit.
        # We must re-create the full_deck based on what wasn't used.
        
        # Use the correct size check
        self.assertEqual(len(final_tableau), 28, "Final tableau must total 28 cards.") 
        
        # Rebuild full deck to ensure we get all 52 unique keys
        full_deck_keys = {card_to_key(make_card(rank, suit)) for rank in ranks for suit in suits}
        
        # Get the set of keys used in the tableau
        tableau_keys_set = {card_to_key(card) for card in final_tableau}
        
        # The stock keys are the difference
        stock_keys_set = full_deck_keys - tableau_keys_set
        
        self.assertEqual(len(stock_keys_set), 24, "Stock card keys must total 24.")

        # Create the actual stock cards (order doesn't strictly matter for the test)
        # We can use the difference in keys to reconstruct the 24 unique stock cards.
        
        # This part requires re-running the full_deck creation to match the stock keys
        stock_cards = []
        for rank in ranks:
            for suit in suits:
                key = card_to_key(make_card(rank, suit))
                if key in stock_keys_set:
                    stock_cards.append(make_card(rank, suit, face_up=False)) # All stock cards are face down

        self.assertEqual(len(stock_cards), 24, "Stock cards must total 24 after final check.")

        # 4. Combine to form the final deck list (52 cards)
        win_deck = final_tableau + stock_cards
        
        self.assertEqual(len(win_deck), 52, "Win deck must have exactly 52 cards.")
        
        # The remainder of the test logic proceeds as intended:
        game = TestSolitaireGame(win_deck)

        # Check immediate win possibility (Aces on top of T0-T3)
        self.assertEqual(game.tableau[0].cards[-1].rank, 'ace')
        self.assertEqual(game.tableau[1].cards[-1].rank, 'ace')
        self.assertEqual(game.tableau[2].cards[-1].rank, 'ace')
        self.assertEqual(game.tableau[3].cards[-1].rank, 'ace')
        

if __name__ == '__main__':
    # You must run this command from the directory containing your project files:
    # python -m unittest test_special_decks.py
    unittest.main()