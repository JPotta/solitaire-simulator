# The “main” script → sets up a game, runs it (either automatically or step by step), 
# prints moves or a simple UI.

from game import SolitaireGame
from pile import Pile
from card import Card

class SolitaireSimulator:
    def __init__(self):
        self.game = SolitaireGame()
        self.moves_made = 0
        
        # START OF CHANGES (REMOVING PROGRESS TRACKING)
        # self.previous_state = None
        # self.no_progress_count = 0
        # END OF CHANGES
        
        # START OF NEW CHANGE: Move History for cycle detection
        self.last_tableau_move = None  # Stores (src_index, dest_index) of the last Tableau-to-Tableau move
        # END OF NEW CHANGE

    def _get_face_up_count(self):
        """Returns the total number of face-up cards in the tableau."""
        count = 0
        for pile in self.game.tableau:
            for card in pile.cards:
                if card.face_up:
                    count += 1
        return count

    def _get_current_state(self):
        """Returns a tuple representing the current board state for progress tracking."""
        # State = (Foundation Score, Face-up Tableau Card Count)
        return (self.get_score(), self._get_face_up_count())

    # START OF NEW METHOD
    def try_stock_draw(self):
        """
        Attempts to draw a card from the stock. 
        Returns True if successful, False if blocked or max passes reached.
        """
        # We rely on game.draw_from_stock to handle the 3-pass check internally.
        if self.game.draw_from_stock():
            self.moves_made += 1
            
            # START OF CHANGE: Reset last tableau move on draw (since it's a new state)
            self.last_tableau_move = None
            # END OF CHANGE
            
            # The stock_passes check assumes game.py exposes this attribute.
            try:
                if self.game.stock_passes > 0 and len(self.game.stock.cards) == 23 and self.moves_made > 28:
                    print(f"[{self.moves_made:03d}] Stock Draw (Pass {self.game.stock_passes})") 
                else:
                    print(f"[{self.moves_made:03d}] Stock Draw.")
            except AttributeError:
                # Fallback if stock_passes isn't explicitly exposed on game.py
                 print(f"[{self.moves_made:03d}] Stock Draw.")
            
            return True
        return False
    # END OF NEW METHOD
        
    def run_simulation(self):
        """Runs the game using a greedy strategy until win, loss, or no moves."""
        print("--- Starting Solitaire Simulation ---")
        
        # START OF CHANGES: Simplifying the loop structure
        while not self.game.is_won() and not self.game.is_lost():
            
            non_draw_move_made = False
            
            # Attempt to make a high-priority non-Draw move
            # We use make_best_non_draw_move (Priority 1-4)
            if self.make_best_non_draw_move():
                non_draw_move_made = True
            
            # If a non-Draw move was made, the loop restarts immediately 
            # (continue) to search for new moves unlocked by the previous one.
            if non_draw_move_made:
                continue
                
            # If no non-Draw move was possible, try to draw a card (Priority 5).
            if self.try_stock_draw():
                # If draw was successful, restart loop to check for newly unlocked moves.
                continue
            
            # If neither a non-Draw move nor a Draw was possible, we are blocked.
            break 
        
        # END OF CHANGES
        
        # FINAL OUTCOME CHECK
        if self.game.is_won():
             print(f"\n✨ WIN! Game completed in {self.moves_made} moves.")
             return True
        # Use the is_lost() method to check for the 3-pass rule violation
        elif self.game.is_lost():
             print(f"\n❌ LOSS: Max passes (3) reached. Game ended after {self.moves_made} moves.")
             return False
        # The game is blocked if it didn't win and wasn't lost by passes.
        else:
             print(f"\n❌ LOSS: Game blocked. No moves possible. Ended after {self.moves_made} moves.")
             return False

    def get_score(self):
        """Returns the total number of cards in the foundations."""
        return sum(len(f.cards) for f in self.game.foundations)

    # START OF NEW METHOD
    def make_best_non_draw_move(self):
        """
        Implements the greedy move strategy without drawing.
        Priority: Foundation > Tableau Sequence > Waste to Tableau
        """
        
        # --- 1. Move from Waste to Foundation ---
        if self.game.waste.cards:
            card = self.game.waste.cards[-1]
            for i, foundation in enumerate(self.game.foundations):
                if self._can_place_foundation_rule(card, foundation):
                    self.game.waste.cards.pop()
                    foundation.add(card)
                    self.moves_made += 1
                    print(f"[{self.moves_made:03d}] Waste ({card.rank}) -> Foundation {i}")
                    # START OF CHANGE: Reset tableau history on non-tableau move
                    self.last_tableau_move = None
                    # END OF CHANGE
                    return True
        
        # --- 2. Move Tableau Top Card to Foundation ---
        for i, tableau_pile in enumerate(self.game.tableau):
            if tableau_pile.cards and tableau_pile.cards[-1].face_up:
                card = tableau_pile.cards[-1]
                for j, foundation in enumerate(self.game.foundations):
                    if self._can_place_foundation_rule(card, foundation):
                        tableau_pile.cards.pop()
                        foundation.add(card)
                        self.flip_top_tableau_card(i)
                        self.moves_made += 1
                        print(f"[{self.moves_made:03d}] Tableau {i} ({card.rank}) -> Foundation {j}")
                        # START OF CHANGE: Reset tableau history on non-tableau move
                        self.last_tableau_move = None
                        # END OF CHANGE
                        return True
        
        # --- 3. Move Tableau Sequence to Tableau (Includes King to Empty) ---
        for src_index, src_pile in enumerate(self.game.tableau):
            if len(src_pile.cards) > 1:
                # Find all possible face-up sequences to move (starting from top to bottom)
                for start_index in range(len(src_pile.cards)):
                    if src_pile.cards[start_index].face_up:
                        sequence = src_pile.cards[start_index:]
                        
                        # Check destination piles
                        for dest_index, dest_pile in enumerate(self.game.tableau):
                            if src_index == dest_index:
                                continue

                            # START OF CRITICAL CHANGE: Cycle Detection
                            # Prevent moving sequence back to the source of the previous move
                            if self.last_tableau_move == (dest_index, src_index):
                                print(f"[BLOCKED] Tableau {src_index} -> Tableau {dest_index}: Preventing direct cycle reversal.")
                                continue
                            # END OF CRITICAL CHANGE

                            if self.game.can_place_tableau_sequence(sequence, dest_pile):
                                # Perform the move
                                src_pile.cards = src_pile.cards[:start_index]
                                dest_pile.add_multiple(sequence)
                                self.flip_top_tableau_card(src_index)
                                self.moves_made += 1
                                print(f"[{self.moves_made:03d}] Tableau {src_index} -> Tableau {dest_index} (Sequence of {len(sequence)})")
                                
                                # START OF CHANGE: Record this move
                                self.last_tableau_move = (src_index, dest_index)
                                # END OF CHANGE
                                
                                return True
        
        # --- 4. Move Waste to Tableau ---
        if self.game.waste.cards:
            card = self.game.waste.cards[-1]
            for i, tableau_pile in enumerate(self.game.tableau):
                if self.game.can_place_tableau(card, tableau_pile):
                    self.game.waste.cards.pop()
                    tableau_pile.add(card)
                    self.moves_made += 1
                    print(f"[{self.moves_made:03d}] Waste ({card.rank}) -> Tableau {i}")
                    # START OF CHANGE: Reset tableau history on non-tableau move
                    self.last_tableau_move = None
                    # END OF CHANGE
                    return True
        
        return False # No non-Draw moves were possible
    # END OF NEW METHOD

    def make_best_move(self):
        """
        DEPRECATED: Now replaced by run_simulation's loop structure and 
        make_best_non_draw_move/try_stock_draw
        """
        # This method is now unused, but kept for context.
        pass

    # --- Helper methods (Copied from GUI/Game for Simulator context) ---

    def _can_place_foundation_rule(self, card, pile):
        """Re-implements the foundation rule check that was only in the GUI."""
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        
        if len(pile.cards) == 0:
            return card.rank == 'ace'
        
        top_card = pile.cards[-1]
        
        return card.suit == top_card.suit and ranks.index(card.rank) == ranks.index(top_card.rank) + 1

    def flip_top_tableau_card(self, pile_index):
        """Flip the top card of a tableau pile if it exists and is face down"""
        pile = self.game.tableau[pile_index]
        if pile.cards and not pile.cards[-1].face_up:
            pile.cards[-1].flip()


if __name__ == "__main__":
    simulator = SolitaireSimulator()
    simulator.run_simulation()
