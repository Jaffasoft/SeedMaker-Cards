import sys
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
import hashlib
import os
import secrets  # Replaced random with secrets for cryptographic security

print("Imports completed")

# Load BIP-39 wordlist
try:
    if os.path.exists("wordlist.txt"):
        with open("wordlist.txt", "r") as f:
            bip39_words = [line.strip() for line in f.readlines()]
        if len(bip39_words) != 2048:
            raise ValueError("Wordlist must contain exactly 2048 words")
    else:
        raise FileNotFoundError("wordlist.txt not found")
except Exception as e:
    print(f"Error loading wordlist: {e}. Using fallback list.")
    bip39_words = ["abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract"] + ["word"] * 2040
print("Wordlist loaded")

class SeedMakerApp(App):
    def build(self):
        print("Starting build...")
        try:
            self.bits = [0] * 132  # 128 + 4 checksum
            self.bit_buttons = []
            self.card_labels = []
            self.word_labels = []
            self.count_labels = []
            self.deck = self.initialize_deck()
            self.dealt_cards = []

            layout = BoxLayout(orientation='vertical', padding=5, spacing=2)
            layout.background_color = [1, 1, 1, 1]
            print("Main layout created")

            # Header
            header = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
            header.background_color = [1, 1, 1, 1]
            self.stats_label = Label(text="0s: 100%  1s: 0%", font_size=20, halign="left", size_hint=(0.33, 1))
            header.add_widget(self.stats_label)
            header.add_widget(Label(text="[b]SeedMaker (Cards)[/b]", markup=True, font_size=20, halign="center", size_hint=(0.33, 1)))
            header.add_widget(Label(text="Warning: Do NOT use for a real seed. Use the print pdf version for 100% offline!", font_size=18, halign="right", size_hint=(0.33, 1)))
            print("Header added")

            # Seed Display
            seed_box = BoxLayout(orientation='vertical', size_hint=(1, 0.1), spacing=5)
            seed_box.add_widget(Label(text="BIP39 Mnemonic 12 Word Seed Phrase", font_size=18, halign="center"))
            self.seed_label = Label(text="", font_size=28, halign="center")
            seed_box.add_widget(self.seed_label)
            print("Seed display added")

            # Controls (dark grey buttons)
            control_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.05))
            control_box.background_color = [1, 1, 1, 1]
            control_box.add_widget(Button(text="Clear", font_size=16, size_hint_y=None, height=40, background_color=[0.3, 0.3, 0.3, 1], on_press=self.clear_bits))
            control_box.add_widget(Button(text="Shuffle Deck and Deal All Cards", font_size=16, size_hint_y=None, height=40, background_color=[0.3, 0.3, 0.3, 1], on_press=self.generate_all_cards))
            control_box.add_widget(Button(text="Copy Seed", font_size=16, size_hint_y=None, height=40, background_color=[0.3, 0.3, 0.3, 1], on_press=self.copy_seed))
            control_box.add_widget(Button(text="Copy Bits", font_size=16, size_hint_y=None, height=40, background_color=[0.3, 0.3, 0.3, 1], on_press=self.copy_bits))
            print("Controls added")

            # Scrollable Grid
            scroll = ScrollView(size_hint=(1, 0.65), bar_width=20, scroll_type=['bars', 'content'])
            scroll.background_color = [1, 1, 1, 1]
            self.grid = GridLayout(cols=26, rows=12, size_hint=(1, None), padding=5, spacing=2)
            self.grid.bind(minimum_height=self.grid.setter('height'))
            self.grid.background_color = [1, 1, 1, 1]
            for row in range(12):
                pairs = 11 if row < 11 else 12
                for col in range(pairs):
                    idx = row * 11 + col
                    if idx < 132:
                        btn = Button(
                            text="0",
                            on_press=lambda instance, i=idx: self.deal_card(i) if i < 128 else self.toggle_checksum(i),
                            background_color=[0.15, 0.15, 0.15, 1] if idx < 128 else [0, 0, 0, 1],
                            color=[1, 1, 1, 1],
                            background_normal='',
                            border=(0, 0, 0, 0) if idx < 128 else (2, 2, 2, 2),
                            size_hint=(1, None),
                            width=80,
                            height=45
                        )
                        self.grid.add_widget(btn)
                        self.bit_buttons.append(btn)
                        if idx < 128:
                            card_label = Label(
                                text="",
                                font_size=32,
                                halign="center",
                                color=[0.2, 0.2, 0.2, 1],
                                font_name='DejaVuSans',
                                size_hint=(1, None),
                                width=80,
                                height=45
                            )
                            self.grid.add_widget(card_label)
                            self.card_labels.append(card_label)
                        else:
                            self.grid.add_widget(Label(text="", size_hint=(1, None), width=80, height=45))
                spacers = 2 if row < 11 else 0
                for _ in range(spacers):
                    self.grid.add_widget(Label(text="", size_hint=(1, None), width=80, height=45))
                word_label = Label(text="", font_size=20, size_hint=(1, None), width=100, height=45)
                self.grid.add_widget(word_label)
                self.word_labels.append(word_label)
                count_label = Label(text="", font_size=20, size_hint=(1, None), width=100, height=45)
                self.grid.add_widget(count_label)
                self.count_labels.append(count_label)
            scroll.add_widget(self.grid)
            print("Grid added")

            # Bottom
            bottom = BoxLayout(orientation='vertical', size_hint=(1, 0.15), spacing=5)
            bottom.background_color = [1, 1, 1, 1]
            self.status_label = Label(text="128 Binary Bits: " + ''.join(str(bit) for bit in self.bits[:128]), font_size=18)
            bottom.add_widget(self.status_label)
            description_label = Label(
                text="SeedMaker Cards shuffles a 52 deck of cards with 4 Jokers added giving 28 odd & 28 even cards. Any odd card drawn is a 1 bit and any even is a 0 bit.",
                font_size=22,
                halign="center",
                valign="middle",
                text_size=(None, None),
                size_hint=(1, None),
                height=60
            )
            bottom.add_widget(description_label)
            print("Bottom added")

            layout.add_widget(header)
            layout.add_widget(seed_box)
            layout.add_widget(control_box)
            layout.add_widget(scroll)
            layout.add_widget(bottom)  # Corrected from 'custom' to 'bottom'
            print("Layout assembled")

            self.update_display()
            print("Build complete")
            return layout
        except Exception as e:
            print(f"Build crashed: {str(e)}")
            raise

    def initialize_deck(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', "8", '9', '10', 'J', 'Q', 'K', 'A']
        deck = [f"{rank}{suit}" for suit in suits for rank in ranks]
        deck.extend(["Joker"] * 4)
        self.fisher_yates_shuffle(deck)  # Use secure shuffle
        return deck

    def fisher_yates_shuffle(self, deck):
        """Cryptographically secure Fisher-Yates shuffle using secrets module."""
        for i in range(len(deck) - 1, 0, -1):
            j = secrets.randbelow(i + 1)  # Secure random index from 0 to i
            deck[i], deck[j] = deck[j], deck[i]

    def get_card_value(self, card):
        rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, '10': 10, 
                    'J': 11, 'Q': 12, 'K': 13, 'A': 14, 'Joker': 15}
        rank = card if card == "Joker" else card[:-1]
        return rank_map[rank]

    def deal_card(self, index):
        if not self.deck:
            self.deck = self.initialize_deck()
        card = self.deck.pop(0)
        self.dealt_cards = [(i, c) for i, c in self.dealt_cards if i != index]
        self.dealt_cards.append((index, card))
        value = self.get_card_value(card)
        bit = 1 if value % 2 else 0
        self.bits[index] = bit
        self.bit_buttons[index].text = str(bit)
        self.bit_buttons[index].background_color = [0.2, 0.2, 0.2, 1] if bit else [0.3, 0.3, 0.3, 1]
        self.card_labels[index].text = card
        self.card_labels[index].color = [1, 0, 0, 1] if card[-1] in ['♥', '♦'] or card == "Joker" else [0.2, 0.2, 0.2, 1]
        self.update_display()

    def toggle_checksum(self, index):
        pass  # Checksum is read-only

    def generate_all_cards(self, instance):
        self.clear_bits(None)
        targets = list(range(128))
        self.fisher_yates_shuffle(targets)  # Secure shuffle of targets
        self.deal_index = 0
        self.deal_targets = targets
        Clock.schedule_interval(self.deal_random_card, 0.023)

    def deal_random_card(self, dt):
        if self.deal_index < len(self.deal_targets):
            index = self.deal_targets[self.deal_index]
            self.deal_card(index)
            self.deal_index += 1
        else:
            Clock.unschedule(self.deal_random_card)

    def clear_bits(self, instance):
        for i in range(132):
            self.bits[i] = 0
        for btn in self.bit_buttons:
            btn.text = "0"
            idx = self.bit_buttons.index(btn)
            btn.background_color = [0.15, 0.15, 0.15, 1] if idx < 128 else [0, 0, 0, 1]
        for label in self.card_labels:
            label.text = ""
            label.color = [0.2, 0.2, 0.2, 1]
        for label in self.word_labels + self.count_labels:
            label.text = ""
        self.deck = self.initialize_deck()
        self.dealt_cards = []
        self.update_display()

    def copy_seed(self, instance):
        seed = self.seed_label.text
        Clipboard.copy(seed)
        print("Seed copied to clipboard:", seed)

    def copy_bits(self, instance):
        bits = ''.join(str(bit) for bit in self.bits[:128])
        Clipboard.copy(bits)
        print("128 bits copied to clipboard:", bits)

    def update_display(self):
        entropy = ''.join(str(bit) for bit in self.bits[:128])
        self.status_label.text = "128 Binary Bits: " + entropy
        ones_count = self.bits[:128].count(1)
        zeros_count = 128 - ones_count
        percent_ones = (ones_count / 128) * 100
        percent_zeros = (zeros_count / 128) * 100
        self.stats_label.text = f"0s: {percent_zeros:.1f}%  1s: {percent_ones:.1f}%"

        entropy_bytes = int(entropy, 2).to_bytes(16, byteorder='big')
        checksum = hashlib.sha256(entropy_bytes).digest()
        checksum_bits = bin(int.from_bytes(checksum, 'big'))[2:].zfill(256)[:4]
        for i, bit in enumerate(checksum_bits):
            self.bits[128 + i] = int(bit)
            self.bit_buttons[128 + i].text = bit
            self.bit_buttons[128 + i].background_color = [0, 0, 0, 1]

        full_bits = entropy + checksum_bits
        words = []
        for i in range(12):
            idx = int(full_bits[i * 11:(i + 1) * 11], 2)
            if idx < 2048:
                word = bip39_words[idx]
                words.append(word)
                if i < len(self.word_labels):
                    self.word_labels[i].text = word
                    self.count_labels[i].text = str(idx + 1)
        self.seed_label.text = ' '.join(words)

if __name__ == '__main__':
    print("Starting app...")
    try:
        SeedMakerApp().run()
    except Exception as e:
        print(f"App crashed: {str(e)}")
    input("Press Enter to close...")
