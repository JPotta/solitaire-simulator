import tkinter as tk
from game import SolitaireGame  # only import the game class
from card import Card            # if you need to reference Card directly
from pile import Pile            # import Pile for validation
from PIL import Image, ImageTk  # put this at the top of your file with other imports

CARD_WIDTH = 80
CARD_HEIGHT = 120
PADDING = 20
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700
CARD_SPACING = 25

class SolitaireGUI:
    # Initialize GUI
    def __init__(self, root):
        self.root = root
        self.root.title("Solitaire Simulator")

        self.game = SolitaireGame()

        # Load card images
        self.card_images = {}
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']

        # Assign images to cards
        for suit in suits:
            for rank in ranks:
                filename = f'images/{rank}_of_{suit}.png'
                img = Image.open(filename).resize((CARD_WIDTH, CARD_HEIGHT))
                self.card_images[f'{rank}_{suit}'] = ImageTk.PhotoImage(img)

        # Card back
        img_back = Image.open('images/back_of_card.png').resize((CARD_WIDTH, CARD_HEIGHT))
        self.card_back = ImageTk.PhotoImage(img_back)

        # Create main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Create control panel
        self.control_frame = tk.Frame(self.main_frame, bg="darkgreen", height=50)
        self.control_frame.pack(fill="x", padx=10, pady=5)
        self.control_frame.pack_propagate(False)
        
        # Add restart button
        self.restart_button = tk.Button(self.control_frame, text="New Game", 
                                       command=self.restart_game, 
                                       bg="lightblue", font=("Arial", 12, "bold"))
        self.restart_button.pack(side="left", padx=10, pady=5)
        
        # Add counters frame
        self.counters_frame = tk.Frame(self.control_frame, bg="darkgreen")
        self.counters_frame.pack(side="right", padx=10, pady=5)
        
        # Stock counter
        self.stock_label = tk.Label(self.counters_frame, text="Stock: 0", 
                                   bg="darkgreen", fg="white", font=("Arial", 10, "bold"))
        self.stock_label.pack(side="left", padx=5)
        
        # Waste counter
        self.waste_label = tk.Label(self.counters_frame, text="Waste: 0", 
                                   bg="darkgreen", fg="white", font=("Arial", 10, "bold"))
        self.waste_label.pack(side="left", padx=5)

        # Draw Green Background
        self.canvas = tk.Canvas(self.main_frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="darkgreen")
        self.canvas.pack(fill="both", expand=True)

        self.draw_board()
        self.update_counters()
        
        # Initialize drag state
        self.dragging = False
        self.drag_card = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Bind mouse events for drag and drop
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)

    def on_mouse_press(self, event):
        x, y = event.x, event.y
        
        # --- Stock click (draw a card) ---
        stock_x, stock_y = PADDING, PADDING
        if stock_x <= x <= stock_x + CARD_WIDTH and stock_y <= y <= stock_y + CARD_HEIGHT:
            self.game.draw_from_stock()
            self.draw_board()
            self.update_counters()
            return

        # --- Check for draggable cards ---
        # Check waste pile
        waste_x = stock_x + CARD_WIDTH + PADDING
        waste_y = PADDING
        if waste_x <= x <= waste_x + CARD_WIDTH and waste_y <= y <= waste_y + CARD_HEIGHT:
            if self.game.waste.cards:
                self.start_drag('waste', self.game.waste.cards[-1], x, y)
            return

        # Check tableau piles
        for i, pile in enumerate(self.game.tableau):
            pile_x = PADDING + i * (CARD_WIDTH + PADDING)
            pile_y = 2*PADDING + CARD_HEIGHT

            # Check all cards in the pile (from top to bottom)
            for j in range(len(pile.cards) - 1, -1, -1):
                card = pile.cards[j]
                if card.face_up:  # Only allow dragging face-up cards
                    card_x = pile_x
                    card_y = pile_y + j * CARD_SPACING
                    if card_x <= x <= card_x + CARD_WIDTH and card_y <= y <= card_y + CARD_HEIGHT:
                        # Find the bottom of the face-up sequence starting from this card
                        bottom_index = self.find_bottom_face_up_sequence(i, j)
                        self.start_drag('tableau', (i, bottom_index), x, y)
                        return

    def on_mouse_drag(self, event):
        if self.dragging:
            # Update the visual position of the dragged card
            self.draw_board()
            self.draw_dragged_card(event.x, event.y)

    def on_mouse_release(self, event):
        if self.dragging:
            self.end_drag(event.x, event.y)
        self.dragging = False
        self.drag_card = None

    def start_drag(self, source_type, source_data, x, y):
        self.dragging = True
        self.drag_card = (source_type, source_data)
        self.drag_start_x = x
        self.drag_start_y = y
        
        # Calculate offset from card position to mouse position
        if source_type == 'waste':
            waste_x = PADDING + CARD_WIDTH + PADDING
            waste_y = PADDING
            self.drag_offset_x = x - waste_x
            self.drag_offset_y = y - waste_y
        elif source_type == 'tableau':
            pile_index, card_index = source_data
            pile_x = PADDING + pile_index * (CARD_WIDTH + PADDING)
            pile_y = 2*PADDING + CARD_HEIGHT
            card_y = pile_y + card_index * CARD_SPACING
            self.drag_offset_x = x - pile_x
            self.drag_offset_y = y - card_y

    def draw_dragged_card(self, x, y):
        if not self.dragging or not self.drag_card:
            return
            
        source_type, source_data = self.drag_card
        
        if source_type == 'waste':
            card = source_data
            img = self.card_images[f'{card.rank}_{card.suit}']
            # Draw the card at the mouse position with offset
            card_x = x - self.drag_offset_x
            card_y = y - self.drag_offset_y
            self.canvas.create_image(card_x, card_y, image=img, anchor='nw')
        elif source_type == 'tableau':
            pile_index, bottom_index = source_data
            pile = self.game.tableau[pile_index]
            
            # Draw all cards in the sequence from bottom to top
            for i in range(bottom_index, len(pile.cards)):
                card = pile.cards[i]
                img = self.card_images[f'{card.rank}_{card.suit}']
                card_x = x - self.drag_offset_x
                card_y = y - self.drag_offset_y + (i - bottom_index) * CARD_SPACING
                self.canvas.create_image(card_x, card_y, image=img, anchor='nw')

    def end_drag(self, x, y):
        if not self.drag_card:
            return
            
        source_type, source_data = self.drag_card
        
        # Check if dropping on a valid target
        target = self.get_drop_target(x, y)
        if target:
            self.perform_move(source_type, source_data, target)
        
        self.draw_board()
        self.update_counters()

    def get_drop_target(self, x, y):
        # Check foundations
        for i, pile in enumerate(self.game.foundations):
            pile_x = 600 + i * (CARD_WIDTH + PADDING)
            pile_y = PADDING
            if pile_x <= x <= pile_x + CARD_WIDTH and pile_y <= y <= pile_y + CARD_HEIGHT:
                return ('foundation', i)
        
        # Check tableau piles
        for i, pile in enumerate(self.game.tableau):
            pile_x = PADDING + i * (CARD_WIDTH + PADDING)
            pile_y = 2*PADDING + CARD_HEIGHT
            if pile_x <= x <= pile_x + CARD_WIDTH and pile_y <= y <= pile_y + 400:
                return ('tableau', i)
        
        return None

    def perform_move(self, source_type, source_data, target):
        target_type, target_index = target
        
        if source_type == 'waste':
            card = source_data
            if target_type == 'foundation':
                if self.can_place_foundation(card, self.game.foundations[target_index]):
                    self.game.waste.cards.pop()
                    self.game.foundations[target_index].add(card)
            elif target_type == 'tableau':
                if self.can_place_tableau(card, self.game.tableau[target_index]):
                    self.game.waste.cards.pop()
                    self.game.tableau[target_index].add(card)
        
        elif source_type == 'tableau':
            pile_index, bottom_index = source_data
            if target_type == 'foundation':
                # Only move the top card to foundation
                top_card_index = len(self.game.tableau[pile_index].cards) - 1
                card = self.game.tableau[pile_index].cards[top_card_index]
                if self.can_place_foundation(card, self.game.foundations[target_index]):
                    self.game.tableau[pile_index].cards.pop(top_card_index)
                    self.game.foundations[target_index].add(card)
                    # Flip the new top card if it exists and is face down
                    self.flip_top_tableau_card(pile_index)
            elif target_type == 'tableau' and target_index != pile_index:
                cards_to_move = self.game.tableau[pile_index].cards[bottom_index:]
                if self.game.can_place_tableau_sequence(cards_to_move, self.game.tableau[target_index]):
                    self.game.tableau[pile_index].cards = self.game.tableau[pile_index].cards[:bottom_index]
                    self.game.tableau[target_index].add_multiple(cards_to_move)
                    # Flip the new top card if it exists and is face down
                    self.flip_top_tableau_card(pile_index)


    # Draw board function
    def draw_board(self):
        self.canvas.delete("all")

        # Draw foundations (top right)
        for i, foundation in enumerate(self.game.foundations):
            x = 600 + i * (CARD_WIDTH + PADDING)
            y = PADDING
            self.draw_slot(x, y, pile=foundation)

        # Draw stock and waste (top left)
        self.draw_slot(PADDING, PADDING, pile=self.game.stock)
        self.draw_slot(PADDING + CARD_WIDTH + PADDING, PADDING, pile=self.game.waste)

        # Draw tableau piles
        for i, tableau_pile in enumerate(self.game.tableau):
            x = PADDING + i * (CARD_WIDTH + PADDING)
            y = 2*PADDING + CARD_HEIGHT
            self.draw_slot(x, y, pile=tableau_pile, vertical_spacing=20)

    # Draw top left pile (slot)
    def draw_slot(self, x, y, pile=None, vertical_spacing=0):
        # Draw empty rectangle if pile is empty
        self.canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT, outline="white", width=2, dash=(4,2))
        if pile:
            for i, card in enumerate(pile.cards):
                img = self.card_images[f'{card.rank}_{card.suit}'] if card.face_up else self.card_back
                self.canvas.create_image(x, y + i*vertical_spacing, image=img, anchor='nw')

    def can_place_foundation(self, card, pile):
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        if len(pile.cards) == 0:
            return card.rank == 'ace'
        top_card = pile.cards[-1]
        return card.suit == top_card.suit and ranks.index(card.rank) == ranks.index(top_card.rank) + 1

    def can_place_tableau(self, card, pile):
        return self.game.can_place_tableau(card, pile)

    def flip_top_tableau_card(self, pile_index):
        """Flip the top card of a tableau pile if it exists and is face down"""
        pile = self.game.tableau[pile_index]
        if pile.cards and not pile.cards[-1].face_up:
            pile.cards[-1].flip()

    def restart_game(self):
        """Restart the game with a new deck"""
        self.game = SolitaireGame()
        self.dragging = False
        self.drag_card = None
        self.draw_board()
        self.update_counters()

    def update_counters(self):
        """Update the stock and waste pile counters"""
        stock_count = len(self.game.stock.cards)
        waste_count = len(self.game.waste.cards)
        self.stock_label.config(text=f"Stock: {stock_count}")
        self.waste_label.config(text=f"Waste: {waste_count}")

    def find_bottom_face_up_sequence(self, pile_index, start_index):
        """Find the bottom card of a valid face-up sequence starting from start_index"""
        pile = self.game.tableau[pile_index]
        bottom_index = start_index
        
        # Walk down the pile to find the bottom of the valid sequence
        for i in range(start_index + 1, len(pile.cards)):
            if not pile.cards[i].face_up:
                break
            # Check if the previous card can be placed on this card (moving down the sequence)
            # This validates that cards[i-1] can be placed on cards[i]
            if self.game.can_place_tableau(pile.cards[i-1], Pile([pile.cards[i]])):
                bottom_index = i
            else:
                break
                
        return bottom_index

if __name__ == "__main__":
    root = tk.Tk()
    gui = SolitaireGUI(root)
    root.mainloop()
