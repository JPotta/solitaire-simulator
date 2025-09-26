solitaire-simulator
Solitaire Simulation for Capstone Assignment

Files
card.py: Defines the Card class, which represents a single playing card.

deck.py: Defines the Deck class, which manages the deck of 52 cards, including shuffling and drawing.

pile.py: Defines the Pile class, a generic container for cards used for the tableau, foundations, stock, and waste piles.

game.py: Defines the SolitaireGame class, which contains the core logic for the game, including dealing, rules for valid moves, and checking for a win or loss.

simulator.py: The main script for the project. It contains a simple "AI" for making moves, functions to simulate a game, and the code to run a large-scale simulation to estimate the win rate. It also includes special test cases for a guaranteed win and a guaranteed loss.

gui.py: Provides a basic graphical user interface for playing the game manually. This is for demonstration and debugging purposes.