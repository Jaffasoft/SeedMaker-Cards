# SeedMaker-Cards
Uses a deck of common script simulated repeating randomly generated 52 deck playing cards with 4 jokers added to make it unbiased and creates BIP39 Mnemonic 12 or 24 words seed phrases. 


WARNING do not use this script for any online wallet seed generation or any seed generation at all for that matter. Unless you know exactly what you are doing and axcept the risks. You should alway do a seed 100% offline and i suggest use the print version so it is randomly worked out using dice or cards or flipping a coin and pen and paper to work the seed out. I have provided pdf versions for this very way. 



Secure Randomness:
Replaced import random with import secrets.

Added fisher_yates_shuffle method using secrets.randbelow for cryptographically secure shuffling.

Updated initialize_deck and generate_all_cards to use this secure shuffle.

The secrets module ensures high-entropy randomness from the OS’s CSPRNG, meeting Bitcoin’s 128-bit (or higher) entropy requirement.

Entropy Guarantee: With 56 cards, a secure shuffle provides ~237 bits of entropy, which is more than enough for BIP-39’s 128-bit standard. The odd/even mapping extracts 128 bits securely.

Verification
Security: The use of secrets ensures unpredictability, making it infeasible for an attacker to reverse-engineer the shuffle or seed, aligning with Bitcoin cryptography standards.

Correctness: The Fisher-Yates algorithm remains unbiased, and the app’s functionality (dealing cards, generating seeds) is preserved.

This script should now be both visually updated and cryptographically secure for your purposes. 


WARNING do not use this script for any online wallet seed generation or any seed generation at all for that matter. Unless you know exactly what you are doing and axcept the risks. You should alway do a seed 100% offline and i suggest use the print version so it is randomly worked out using dice or cards or flipping a coin and pen and paper to work the seed out. I have provided pdf versions for this very way. 



Entropy and Checksum: BIP-39 specifies 256 bits of entropy + 8 bits of checksum for a 24-word phrase (11 bits per word × 24 = 264 bits).

UI Adjustments: The grid will need to accommodate 264 bits (256 entropy + 8 checksum) and display 24 words. We'll adjust the layout to 26 columns and 24 rows (with some spacers).

Card Deck: We'll still use the 56-card deck (52 + 4 Jokers), which provides ~237 bits of entropy per full shuffle. To get 256 bits, we'll deal additional cards as needed, ensuring cryptographic randomness.


24 Word Cards Seed Notes:

Key Modifications
Class Name: Changed to SeedMaker24App to distinguish it from the 12-word version.

Bit Array: Increased to 264 bits (self.bits = [0] * 264).

Grid Layout: Adjusted to 24 rows, with 11 bit/card pairs for rows 0-22 and 12 for row 23 (to fit 256 + 8 bits).

Entropy and Checksum: 
256 bits of entropy, extracted from card deals.

8-bit checksum computed via SHA-256 (per BIP-39).

UI Tweaks: 
Adjusted size_hint values (scroll to 0.6, seed_box to 0.15) to fit the larger grid and seed phrase.

Reduced seed_label font size to 24 and added height constraints to fit 24 words.

Card Dealing: Deals 256 cards (reshuffling the deck ~4.5 times), ensuring 256 bits of entropy from the secure secrets-based shuffle.

Word Generation: Loops 24 times to generate the 24-word phrase.

Notes
Entropy: The 56-card deck provides ~237 bits per shuffle. Dealing 256 cards requires multiple shuffles, but the secrets module ensures each shuffle is cryptographically secure, cumulatively providing well over 256 bits of entropy.

File Name: Save this as a separate file, e.g., seedmaker_24.py, to keep it distinct from the 12-word version.

This script is ready to run and will generate a secure 24-word BIP-39 seed phrase. 

BIP-39 standards

hardware wallets


Disclaimer: I accept no responsibility for loss of crypto funds from any crypto wallet or hardware wallet as a result of using this script to make a seed phrase. This script is for learning purposes only. Do not use to make a real seed for any real crypto wallet. 



