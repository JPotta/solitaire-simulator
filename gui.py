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


		# Drag-and-drop state
		self.selected_card = None
		self.id_to_card_info = {}
		self.pile_slots = []  # list of dicts: {type, index, rect: (x1,y1,x2,y2)}
		self.drag_data = None  # dict with current drag info

		self.draw_board()

		# Mouse bindings for drag-and-drop
		self.canvas.bind("<Button-1>", self.on_mouse_down)
		self.canvas.bind("<B1-Motion>", self.on_mouse_move)
		self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

	def on_mouse_down(self, event):
		x, y = event.x, event.y
		self.drag_data = None

		# Identify topmost canvas item under cursor
		items = self.canvas.find_overlapping(x, y, x, y)
		if items:
			item_id = items[-1]
			info = self.id_to_card_info.get(item_id)
			if info:
				pile_type = info['type']
				pile_index = info['index']
				card_index = info['card_index']
				# Clicking stock draws a card
				if pile_type == 'stock':
					self.game.draw_from_stock()
					self.draw_board()
					return
				# Waste: only top card is draggable
				if pile_type == 'waste':
					if card_index == len(self.game.waste.cards) - 1:
						self.drag_data = {
							'source': 'waste',
							'src_index': None,
							'card_index': card_index,
							'cards': [self.game.waste.cards[-1]],
							'canvas_ids': [item_id],
							'last_x': x,
							'last_y': y,
						}
					return
				# Tableau: only face-up cards; drag stack from clicked card
				if pile_type == 'tableau':
					card_obj = self.game.tableau[pile_index].cards[card_index]
					if not card_obj.face_up:
						return
					cards_to_move = self.game.tableau[pile_index].cards[card_index:]
					# gather canvas ids for the moving stack
					moving_ids = [cid for cid, meta in self.id_to_card_info.items() if meta['type'] == 'tableau' and meta['index'] == pile_index and meta['card_index'] >= card_index]
					# sort ids by card_index to preserve order
					moving_ids.sort(key=lambda cid: self.id_to_card_info[cid]['card_index'])
					self.drag_data = {
						'source': 'tableau',
						'src_index': pile_index,
						'card_index': card_index,
						'cards': cards_to_move,
						'canvas_ids': moving_ids,
						'last_x': x,
						'last_y': y,
					}
					return

		# If clicking on empty stock area, draw a card
		stock_x, stock_y = PADDING, PADDING
		if stock_x <= x <= stock_x + CARD_WIDTH and stock_y <= y <= stock_y + CARD_HEIGHT:
			self.game.draw_from_stock()
			self.draw_board()
			return

	def on_mouse_move(self, event):
		if not self.drag_data:
			return
		dx = event.x - self.drag_data['last_x']
		dy = event.y - self.drag_data['last_y']
		for cid in self.drag_data['canvas_ids']:
			self.canvas.move(cid, dx, dy)
		self.drag_data['last_x'] = event.x
		self.drag_data['last_y'] = event.y

	def on_mouse_up(self, event):
		if not self.drag_data:
			return
		x, y = event.x, event.y
		source = self.drag_data['source']
		src_index = self.drag_data['src_index']
		cards = list(self.drag_data['cards'])

		# Determine drop target by slot rectangles
		drop_target = None
		for slot in self.pile_slots:
			x1, y1, x2, y2 = slot['rect']
			if x1 <= x <= x2 and y1 <= y <= y2:
				drop_target = slot
				break

		moved = False
		if drop_target:
			if drop_target['type'] == 'tableau':
				dest_idx = drop_target['index']
				dest_pile = self.game.tableau[dest_idx]
				if self.game.can_place_tableau(cards[0], dest_pile):
					# remove from source
					if source == 'waste':
						self.game.waste.cards.pop()
					elif source == 'tableau':
						self.game.tableau[src_index].cards = self.game.tableau[src_index].cards[:self.drag_data['card_index']]
						# flip new top if face down
						if self.game.tableau[src_index].cards and not self.game.tableau[src_index].cards[-1].face_up:
							self.game.tableau[src_index].cards[-1].flip()
					# add to destination
					dest_pile.cards.extend(cards)
					moved = True
			elif drop_target['type'] == 'foundation' and len(cards) == 1:
				dest_idx = drop_target['index']
				dest_pile = self.game.foundations[dest_idx]
				if self.can_place_foundation(cards[0], dest_pile):
					if source == 'waste':
						self.game.waste.cards.pop()
					elif source == 'tableau':
						self.game.tableau[src_index].cards = self.game.tableau[src_index].cards[:self.drag_data['card_index']]
						if self.game.tableau[src_index].cards and not self.game.tableau[src_index].cards[-1].face_up:
							self.game.tableau[src_index].cards[-1].flip()
					self.game.foundations[dest_idx].add(cards[0])
					moved = True

		# Redraw to snap to final positions (moved or not)
		self.drag_data = None
		self.draw_board()


	# Draw board function
    def draw_board(self):
		self.canvas.delete("all")
		self.id_to_card_info = {}
		self.pile_slots = []

		# Draw foundations (top right)
        for i, foundation in enumerate(self.game.foundations):
			x = 600 + i * (CARD_WIDTH + PADDING)
			y = PADDING
			self.pile_slots.append({'type': 'foundation', 'index': i, 'rect': (x, y, x + CARD_WIDTH, y + CARD_HEIGHT)})
			self.draw_slot(x, y, pile=foundation, vertical_spacing=0, pile_type='foundation', pile_index=i)

		# Draw stock and waste (top left)
		stock_x, stock_y = PADDING, PADDING
		waste_x, waste_y = PADDING + CARD_WIDTH + PADDING, PADDING
		self.pile_slots.append({'type': 'stock', 'index': None, 'rect': (stock_x, stock_y, stock_x + CARD_WIDTH, stock_y + CARD_HEIGHT)})
		self.pile_slots.append({'type': 'waste', 'index': None, 'rect': (waste_x, waste_y, waste_x + CARD_WIDTH, waste_y + CARD_HEIGHT)})
		self.draw_slot(stock_x, stock_y, pile=self.game.stock, vertical_spacing=0, pile_type='stock', pile_index=None)
		self.draw_slot(waste_x, waste_y, pile=self.game.waste, vertical_spacing=0, pile_type='waste', pile_index=None)

		# Draw tableau piles
        for i, tableau_pile in enumerate(self.game.tableau):
			x = PADDING + i * (CARD_WIDTH + PADDING)
			y = 2*PADDING + CARD_HEIGHT
			# Extended drop area for tableau columns
			self.pile_slots.append({'type': 'tableau', 'index': i, 'rect': (x, y, x + CARD_WIDTH, y + CARD_HEIGHT + 400)})
			self.draw_slot(x, y, pile=tableau_pile, vertical_spacing=20, pile_type='tableau', pile_index=i)

	# Draw pile (slot)
	def draw_slot(self, x, y, pile=None, vertical_spacing=0, pile_type=None, pile_index=None):
		# Draw empty rectangle
		self.canvas.create_rectangle(x, y, x + CARD_WIDTH, y + CARD_HEIGHT, outline="white", width=2, dash=(4,2))
		if pile:
			for i, card in enumerate(pile.cards):
				img = self.card_images[f'{card.rank}_{card.suit}'] if card.face_up else self.card_back
				item_id = self.canvas.create_image(x, y + i*vertical_spacing, image=img, anchor='nw')
				if pile_type is not None:
					self.id_to_card_info[item_id] = {
						'type': pile_type,
						'index': pile_index,
						'card_index': i,
						'card': card,
					}

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
