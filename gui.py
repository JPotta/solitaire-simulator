import tkinter as tk
from game import SolitaireGame  # only import the game class
from card import Card            # if you need to reference Card directly
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

        # Draw Green Background
        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="darkgreen")
        self.canvas.pack(fill="both", expand=True)

        self.draw_board()
        # Bind Click Button
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        x, y = event.x, event.y

        # --- Stock click (draw a card) ---
        stock_x, stock_y = PADDING, PADDING
        if stock_x <= x <= stock_x + CARD_WIDTH and stock_y <= y <= stock_y + CARD_HEIGHT:
            self.game.draw_from_stock()
            self.draw_board()
            return

        # --- Waste click (select top card) ---
        waste_x = stock_x + CARD_WIDTH + PADDING
        waste_y = PADDING
        if waste_x <= x <= waste_x + CARD_WIDTH and waste_y <= y <= waste_y + CARD_HEIGHT:
            if self.game.waste.cards:
                self.selected_card = ('waste', self.game.waste.cards[-1])
            return

        # --- Foundation click (place card) ---
        for i, pile in enumerate(self.game.foundations):
            pile_x = 600 + i * (CARD_WIDTH + PADDING)
            pile_y = PADDING
            if pile_x <= x <= pile_x + CARD_WIDTH and pile_y <= y <= pile_y + CARD_HEIGHT:
                if self.selected_card:
                    source = self.selected_card[0]
                    if source == 'waste':
                        card_to_move = self.selected_card[1]
                        if self.can_place_foundation(card_to_move, pile):
                            self.game.waste.cards.pop()
                            pile.add(card_to_move)
                            self.selected_card = None
                            self.draw_board()
                            return
                    elif source == 'tableau':
                        src_pile_index = self.selected_card[1]
                        card_index = self.selected_card[2]
                        card_to_move = self.game.tableau[src_pile_index].cards[card_index]
                        if self.can_place_foundation(card_to_move, pile):
                            self.game.tableau[src_pile_index].cards.pop(card_index)
                            pile.add(card_to_move)
                            self.selected_card = None
                            self.draw_board()
                            return

        # --- Tableau click (select or move) ---
        for i, pile in enumerate(self.game.tableau):
            pile_x = PADDING + i * (CARD_WIDTH + PADDING)
            pile_y = 200  # starting Y for tableau

            # Check all cards in the pile
            for j, card in enumerate(pile.cards):
                card_x = pile_x
                card_y = pile_y + j * CARD_SPACING
                if card_x <= x <= card_x + CARD_WIDTH and card_y <= y <= card_y + CARD_HEIGHT:
                    # Selecting a card
                    self.selected_card = ('tableau', i, j)
                    return

            # If clicking empty tableau space → attempt move
            if pile_x <= x <= pile_x + CARD_WIDTH and pile_y <= y <= pile_y + 400:
                if self.selected_card:
                    source = self.selected_card[0]
                    if source == 'waste':
                        card_to_move = self.selected_card[1]
                        if self.can_place_tableau(card_to_move, pile):
                            self.game.waste.cards.pop()
                            pile.cards.append(card_to_move)
                            self.selected_card = None
                            self.draw_board()
                            return
                    elif source == 'tableau':
                        src_pile_index = self.selected_card[1]
                        card_index = self.selected_card[2]
                        cards_to_move = self.game.tableau[src_pile_index].cards[card_index:]
                        if self.can_place_tableau(cards_to_move[0], pile):
                            self.game.tableau[src_pile_index].cards = self.game.tableau[src_pile_index].cards[:card_index]
                            pile.cards.extend(cards_to_move)
                            self.selected_card = None
                            self.draw_board()
                            return


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

    # 
    def can_place_foundation(self, card, pile):
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']
        if len(pile.cards) == 0:
            return card.rank == 'ace'
        top_card = pile.cards[-1]
        return card.suit == top_card.suit and ranks.index(card.rank) == ranks.index(top_card.rank) + 1

if __name__ == "__main__":
    root = tk.Tk()
    gui = SolitaireGUI(root)
    root.mainloop()
