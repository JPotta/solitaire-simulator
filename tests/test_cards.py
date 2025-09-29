import unittest
from card import Card

class TestCard(unittest.TestCase):
    """Tests for the Card class."""
    
    def make_card(self, rank, suit, face_up=False):
        """Utility to quickly create a Card object."""
        return Card(rank, suit, face_up=face_up)

    def test_initialization(self):
        """Test card initialization of rank, suit, and face_up state."""
        card1 = self.make_card('ace', 'spades', face_up=True)
        self.assertEqual(card1.rank, 'ace')
        self.assertEqual(card1.suit, 'spades')
        self.assertTrue(card1.face_up)
        
    def test_flip_method(self):
        """Test that the flip method correctly toggles the face_up state."""
        card = self.make_card('2', 'hearts', face_up=False)
        self.assertFalse(card.face_up)
        
        card.flip()
        self.assertTrue(card.face_up)
        
        card.flip()
        self.assertFalse(card.face_up)


if __name__ == '__main__':
    unittest.main()