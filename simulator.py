# The “main” script → sets up a game, runs it (either automatically or step by step), 
# prints moves or a simple UI.

import random
from game import SolitaireGame
from deck import Deck
from card import Card

def find_a_move(game):
    """
    A simple "AI" to find and make a single valid move.
    Returns True if a move was made, False otherwise.
    """
    # 1. Check for moves from Waste to Foundation
    if game.can_move_waste_to_foundation():
        game.move_waste_to_foundation()
        print("Moved card from waste to foundation.")
        return True

    # 2. Check for moves from Tableau to Foundation
    for i in range(7):
        if game.can_move_tableau_to_foundation(i):
            game.move_tableau_to_foundation(i)
            print(f"Moved card from tableau {i} to foundation.")
            return True

    # 3. Check for moves from Waste to Tableau
    for i in range(7):
        if game.can_move_waste_to_tableau(i):
            game.move_waste_to_tableau(i)
            print(f"Moved card from waste to tableau {i}.")
            return True

    # 4. Check for moves from Tableau to Tableau
    for i in range(7):
        # We only consider moving single cards for this simple AI
        if game.tableau[i] and game.tableau[i].peek().face_up:
            for j in range(7):
                if i != j and game.can_move_tableau_to_tableau(i, j, 1):
                    game.move_tableau_to_tableau(i, j, 1)
                    print(f"Moved card from tableau {i} to tableau {j}.")
                    return True
    
    return False

def simulate_game(game):
    """
    Simulates a single game of solitaire with a simple move-finding AI.
    """
    while not game.is_won() and not game.is_lost():
        
        # Try to make a move
        moved = find_a_move(game)
        
        # If no moves were found, draw from the stock
        if not moved:
            if not game.draw_from_stock():
                # No moves found and can't draw anymore, game is lost
                break

    if game.is_won():
        return True
    else:
        return False

def run_simulation(num_games):
    """
    Runs a large-scale simulation to estimate winning percentage.
    """
    wins = 0
    for i in range(num_games):
        game = SolitaireGame()
        if simulate_game(game):
            wins += 1
            print(f"Game {i+1}: WIN")
        else:
            print(f"Game {i+1}: LOSE")
    
    win_percentage = (wins / num_games) * 100
    print(f"\n--- Simulation Results ---")
    print(f"Total Games: {num_games}")
    print(f"Wins: {wins}")
    print(f"Winning Percentage: {win_percentage:.2f}%")
    return win_percentage

def test_guaranteed_win():
    """
    Sets up and tests a guaranteed winnable game.
    A simple winnable game: all cards are sorted into foundations.
    """
    print("\n--- Running Guaranteed Win Test ---")
    # Create a dummy deck to access the ranks attribute
    d = Deck()
    foundations = [
        [Card(r, 'spades') for r in d.ranks],
        [Card(r, 'hearts') for r in d.ranks],
        [Card(r, 'clubs') for r in d.ranks],
        [Card(r, 'diamonds') for r in d.ranks],
    ]
    # Flatten and reverse the list for the deck
    win_deck = [card for foundation in foundations for card in foundation]
    win_deck.reverse()
    
    game = SolitaireGame(shuffled_cards=win_deck)

    # In a guaranteed win, we just need to move from stock/waste to foundation
    # and tableau to foundation.
    while not game.is_won():
        moved = False
        for i in range(7):
            if game.can_move_tableau_to_foundation(i):
                game.move_tableau_to_foundation(i)
                moved = True
        if game.can_move_waste_to_foundation():
            game.move_waste_to_foundation()
            moved = True
        
        if not moved:
            game.draw_from_stock()

    if game.is_won():
        print("Guaranteed win test: SUCCESS")
        return True
    else:
        print("Guaranteed win test: FAILED")
        return False
    
def test_guaranteed_loss():
    """
    Sets up and tests a guaranteed losable game.
    A simple losable game: all Kings are at the bottom of the tableau,
    and all Aces are at the very bottom of the stock.
    """
    print("\n--- Running Guaranteed Loss Test ---")
    d = Deck()
    
    # Put all Kings at the bottom of the tableau
    kings = [Card('king', 'spades'), Card('king', 'hearts'), Card('king', 'clubs'), Card('king', 'diamonds')]
    
    # Put all Aces at the very bottom of the deck
    aces = [Card('ace', 'spades'), Card('ace', 'hearts'), Card('ace', 'clubs'), Card('ace', 'diamonds')]
    
    # Create the rest of the cards
    other_cards = [c for c in d.cards if c.rank != 'king' and c.rank != 'ace']
    random.shuffle(other_cards)
    
    loss_deck = kings + other_cards + aces
    
    game = SolitaireGame(shuffled_cards=loss_deck)

    # In a guaranteed loss, no moves should be possible other than drawing
    while not game.is_won() and not game.is_lost():
        moved = find_a_move(game)
        
        if not moved:
            if not game.draw_from_stock():
                break

    if game.is_lost():
        print("Guaranteed loss test: SUCCESS")
        return True
    else:
        print("Guaranteed loss test: FAILED")
        return False

if __name__ == "__main__":
    test_guaranteed_win()
    test_guaranteed_loss()
    
    # Run the main simulation
    print("\nStarting main simulation...")
    run_simulation(100)
