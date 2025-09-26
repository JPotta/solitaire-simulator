# Holds the Card class → properties like rank, suit, color, 
# plus helpers (e.g., is_red(), __str__() for printing).

class Card:
    # Intialize Card
    def __init__(self, rank, suit, face_up=False):
        self.rank = rank
        self.suit = suit
        self.face_up = face_up

    # Flip card
    def flip(self):
        self.face_up = not self.face_up

    def __repr__(self):
        return f"{self.rank} of {self.suit} ({'up' if self.face_up else 'down'})"