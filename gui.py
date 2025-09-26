import tkinter as tk
from game import SolitaireGame  # only import the game class
from card import Card            # if you need to reference Card directly
from PIL import Image, ImageTk  # put this at the top of your file with other imports

CARD_WIDTH = 80
CARD_HEIGHT = 120
PADDING = 20
CANVAS_WIDTH = 1000
CANVAS_HEIGHT = 700

class SolitaireGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Solitaire Simulator")

        self.game = SolitaireGame()

        # Load card images
        
        self.card_images = {}
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['ace','2','3','4','5','6','7','8','9','10','jack','queen','king']

        for suit in suits:
            for rank in ranks:
                filename = f'images/{rank}_of_{suit}.png'
                img = Image.open(filename).resize((CARD_WIDTH, CARD_HEIGHT))
                self.card_images[f'{rank}_{suit}'] = ImageTk.PhotoImage(img)

# Card back
        img_back = Image.open('images/back_of_card.png').resize((CARD_WIDTH, CARD_HEIGHT))
        self.card_back = ImageTk.PhotoImage(img_back)

        self.canvas = tk.Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="darkgreen")
        self.canvas.pack(fill="both", expand=True)

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def on_click(self, event):
        # Click anywhere on stock to draw a card
        stock_x = PADDING
        stock_y = PADDING
        if stock_x <= event.x <= stock_x + CARD_WIDTH and stock_y <= event.y <= stock_y + CARD_HEIGHT:
            self.game.draw_from_stock()
            self.draw_board()

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

    def draw_slot(self, x, y, pile=None, vertical_spacing=0):
        # Draw empty rectangle if pile is empty
        self.canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT,
                                     outline="white", width=2, dash=(4,2))
        if pile:
            for i, card in enumerate(pile.cards):
                img = self.card_images[f'{card.rank}_{card.suit}'] if card.face_up else self.card_back
                self.canvas.create_image(x, y + i*vertical_spacing, image=img, anchor='nw')

if __name__ == "__main__":
    root = tk.Tk()
    gui = SolitaireGUI(root)
    root.mainloop()
