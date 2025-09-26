# Holds the Card class -> properties like rank, suit, color, 
# plus helpers (e.g., is_red(), __str__() for printing).

class Card:
    """
    Represents a single playing card with a rank, suit, and face-up state.
    """
    def __init__(self, rank, suit, face_up=False):
        """
        Initializes a Card object.

        Args:
            rank (str): The rank of the card (e.g., 'ace', 'king', '2').
            suit (str): The suit of the card (e.g., 'hearts', 'spades').
            face_up (bool): True if the card is face up, False otherwise.
        """
        self.rank = rank
        self.suit = suit
        self.face_up = face_up

    def get_color(self):
        """
        Returns the color of the card based on its suit.
        """
        if self.suit in ['hearts', 'diamonds']:
            return 'red'
        else:
            return 'black'

    def get_value(self):
        """
        Returns the numerical value of the card for comparisons.
        Ace is 1, Jack is 11, Queen is 12, King is 13.
        """
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        return ranks.index(self.rank) + 1

    def flip(self):
        """
        Flips the card's face-up state.
        """
        self.face_up = not self.face_up

    def __repr__(self):
        """
        Provides a string representation of the card.
        """
        return f"{self.rank} of {self.suit} ({'up' if self.face_up else 'down'})"
