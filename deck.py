
# Holds the Deck class → creates 52 Card objects, shuffles, 
# or sets up a special test order. Exposes draw() to pull cards.

import random

def fisher_yates_shuffle(arr):
    """
    Shuffles an array in-place using the Fisher-Yates algorithm.
    """
    n = len(arr)
    # Start from the last element and move backwards.
    for i in range(n - 1, 0, -1):
        # Pick a random index from 0 to i (inclusive).
        j = random.randint(0, i)

        # Swap the element at the current position (i) with the
        # element at the random position (j).
        arr[i], arr[j] = arr[j], arr[i]

    return arr

# Example usage
my_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
print(f"Original list: {my_list}")
shuffled_list = fisher_yates_shuffle(my_list)
print(f"Shuffled list: {shuffled_list}")

# Another example with a different data type
card_deck = ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2']
print(f"Original deck: {card_deck}")
shuffled_deck = fisher_yates_shuffle(card_deck)
print(f"Shuffled deck: {shuffled_deck}")

