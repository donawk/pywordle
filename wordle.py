# BismiAllah
from english_words import english_words_lower_alpha_set
from random import choice
from json import dump, load
from os.path import exists

ALL_WORDS = english_words_lower_alpha_set
FIVE_LETTER_WORDS = list(filter(lambda x: len(x) == 5, list(ALL_WORDS)))
WORDLES = [word.upper() for word in FIVE_LETTER_WORDS]

# CORRECT = '🟢'🟧 
ABSENT = '🟥' 
PRESENT = '🟨' 
CORRECT = '🟩'
UNKNOWN = '❓'
BLANK = '➖'

ABSENT_LETTER = ' '

PASS_SYMBOLS = ['🟣', '🔵', '🟢', '🟡', '🟠', '🔴']
FAIL_SYMBOL = '🔘'
STATUS_SYMBOLS = {str(x): PASS_SYMBOLS[x-1] for x in range(1,7)}
STATUS_SYMBOLS['F'] = FAIL_SYMBOL
# list(reversed([symbol for symbol in "🔘🔴🟠🟡🟢🔵🟣"]))

WINNING_STATE = ['🟩' for _ in range(5)]

LETTERS_1ST_ROW = [letter for letter in 'QWERTYUIOP']
LETTERS_2ND_ROW = [letter for letter in 'ASDFGHJKL']
LETTERS_3RD_ROW = [letter for letter in 'ZXCVBNM']

SCORES_FILE = 'scores.json'

def show_previous_scores(previous_scores):
    for attempt_status in previous_scores:
        if attempt_status == "F":
            symbol = STATUS_SYMBOLS['F']
            attempts = 'F'
        else:
            symbol = STATUS_SYMBOLS[attempt_status]
            attempts = attempt_status
        attempt_dist = previous_scores[attempt_status]
        print(attempts + ':', symbol * attempt_dist, '|', attempt_dist)

def init_previous_scores():
    scores = {str(x): 0 for x in range(1, 7)}
    scores['F'] = 0
    with open(SCORES_FILE, 'w') as file:
        dump(scores, file)
    return scores

def get_previous_scores():
    if exists(SCORES_FILE):
        with open(SCORES_FILE, 'r') as file:
            previous_scores = load(file)
    else:
        previous_scores = init_previous_scores()
    return previous_scores

def set_previous_scores(scores, attempt):
    if attempt != 'F':
        score = str(6 - attempt)
    else: score = attempt
    scores[score] = scores[score] + 1
    with open(SCORES_FILE, 'w') as file:
        dump(scores, file)

def show_letter_tracker(letter_tracker):
    rows = letter_tracker['rows']
    print("Unused letters:")
    for i, row in enumerate(rows):
        print(' '*i, ' '.join(row))

def update_letter_tracker(letter_tracker, guess):
    seen = letter_tracker['seen']
    rows = letter_tracker['rows']
    for letter in guess:
        if letter not in seen:
            seen.append(letter)
            for row in rows:
                if letter in row:
                    row[row.index(letter)] = ABSENT_LETTER
                    break
    return {'seen': seen, 'rows': rows}

def init_letter_tracker():
    rows = [LETTERS_1ST_ROW[:], LETTERS_2ND_ROW[:], LETTERS_3RD_ROW[:]]
    return {'seen': [], 'rows': rows}

def show_game(guess, corrections):
    print(' ', '  '.join(guess))
    print('', ' '.join(corrections))

def find_max_depth(present_letters):
    # print("PRESENT LETTERS:", present_letters)
    return max([len(row) for row in present_letters.values()])

def show_correct_letters(correct_letters):
    print("Correct so far:")
    show_game(correct_letters, [CORRECT if letter != ABSENT_LETTER else BLANK for letter in correct_letters])

def show_present_letters(present_letters):
    # print("Found so far:")
    # print("PRESENT LETTERS:", present_letters)
    markers = []
    for col in range(5):
        if present_letters[col]:
            markers.append(PRESENT)
        else:
            markers.append(UNKNOWN)
    print('', ' '.join(markers))

    for depth in range(find_max_depth(present_letters)):
        # print("DEPTH:", depth)
        found_letters = []
        for col in range(5):
            # print(" COL:", col, " LEN:", len(present_letters[col]))
            if depth < len(present_letters[col]):
                found_letters.append(present_letters[col][depth])
            else:
                found_letters.append(' ')
        
        print(' ', '  '.join(found_letters))

def show_rest(absent_letters, letter_tracker, attempts):
    unguessed_letters = sorted([x for row in letter_tracker['rows'] for x in row if x != ABSENT_LETTER])
    absent_letters = sorted(absent_letters) # don't remember if .sort() is a thing
    
    print(UNKNOWN + ":", ' '.join(unguessed_letters))
    print(ABSENT + ':', ' '.join(absent_letters))
    print(attempts, f"attempt{('s', '')[attempts == 1]} left.")

def show_hint(guessed_letters, letter_tracker, attempts):
    correct_letters, present_letters, absent_letters = guessed_letters.values()
    show_correct_letters(correct_letters)
    show_present_letters(present_letters)
    show_rest(absent_letters, letter_tracker, attempts)

def select_new_word():
    return choice(WORDLES).upper()

def get_corrections(guess, word):
    symbols = []
    correct_letters = [] 
    present_letters = [] 
    absent_letters = []
    for i, l in enumerate(guess):
        if l == word[i]:
            correct_letters.append(l)
            present_letters.append(ABSENT_LETTER)
            symbols.append(CORRECT)
        elif l in word:
            correct_letters.append(ABSENT_LETTER)
            present_letters.append(l)
            symbols.append(PRESENT)
        else:
            correct_letters.append(ABSENT_LETTER)
            present_letters.append(ABSENT_LETTER)
            absent_letters.append(l)
            symbols.append(ABSENT)
    return {'symbols': symbols, 'correct': correct_letters, 'present': present_letters, 'absent': absent_letters}

def sort_corrections(corrections, guessed_letters):
    # print("Corrections:")
    # print(corrections, '\nJUMP\n')
    _, new_correct_letters, new_present_letters, new_absent_letters = corrections.values()
    for i, letter in enumerate(new_correct_letters):
        if letter != ABSENT_LETTER:
            guessed_letters['correct'][i] = letter
    # print("New Present Letters:", new_present_letters)
    for i, letter in enumerate(new_present_letters):
        if letter != ABSENT_LETTER and letter not in guessed_letters['present'][i]:
            guessed_letters['present'][i].append(letter)
    # guessed_letters['present'] = list(set(guessed_letters['present'] + new_present_letters))
    guessed_letters['absent'] = list(set(guessed_letters['absent'] + new_absent_letters))
    return guessed_letters

def get_correctness(guess, word):
    return guess == word

def init_guessed_letters():
    correct_letters = [ABSENT_LETTER] * 5
    present_letters = {x: [] for x in range(5)}
    absent_letters = []
    return {'correct': correct_letters, 'present': present_letters, 'absent': absent_letters}

def get_guess(guessed_letters, guessed_words, letter_tracker, attempts):
    while True:
        guess = input("Enter guess:\n").upper()
        if guess == '-':
            return 0
        elif guess == '?':
            show_hint(guessed_letters, letter_tracker, attempts)
        elif guess in guessed_words:
            print("Word has already been guessed.")
        elif len(guess) != 5:
            print("Guess has to be a word of five letters.")
        elif guess not in WORDLES:
            print("Word not found!")
        else:
            return guess

def welcome_message():
    print(
f'''
Assalamu alaikum, and welcome to Wordle, where you have to guess a five-letter word to win.
You have six chances to guess that word, and you'll be told how close you are along the way.
{ABSENT} Means the letter isn't in the word
{PRESENT} Means the letter is in the word, but not where you placed it
{CORRECT} Means the letter is in the word, and where you placed it
- Guess "?" to show a hint, which is your progress for finding the word.
- Guess '-' to give up on your current word (will count as a loss).
May Allah guide you, and have fun!
'''
    )

def wordle():
    print()

    attempts = 6
    win = False

    word = select_new_word()
    letter_tracker = init_letter_tracker()
    guessed_letters = init_guessed_letters()
    guessed_words = []

    while attempts > 0:
        show_letter_tracker(letter_tracker)
        guess = get_guess(guessed_letters, guessed_words, letter_tracker, attempts)
        if not guess:
            break
        guessed_words.append(guess)

        attempts = attempts - 1
        if get_correctness(guess, word):
            show_game(guess, WINNING_STATE)
            win = True
            break
        else:
            letter_tracker = update_letter_tracker(letter_tracker, guess)
            corrections = get_corrections(guess, word)
            guessed_letters = sort_corrections(corrections, guessed_letters)
            show_game(guess, corrections['symbols'])
            print(attempts, f"attempt{('s', '')[attempts==1]} left.")
    
    if win:
        print(f"MashaAllah, you did it in {6 - attempts} tr{('y', 'ies')[attempts<5]}.")
    else:
        attempts = 'F'
        print("May you triumph the next time, Akhi.")
        print("The word was", word)

    set_previous_scores(get_previous_scores(), attempts)
    show_previous_scores(get_previous_scores())

if __name__ == "__main__":
    welcome_message()
    input("Press ENTER TO PROCEED.\n (Ctrl+Z to Quit at any time.)\n  ")

    wordle()
    while input("Play again? (y/n): ").lower() == 'y':
        wordle()
###
# TODO:
# DONE: Add history with '?' input
# DONE: Add leave game option with '-' input
# DONE: Add previous games scores, which is shown when a game ends
# DONE: Reformat STATUS_SYMBOL assignment to make it more intuitive (dict comprehension)
# DONE: Update show_hints to show where the 'present' letters were found, rather than list them.
# DONE: Edit imports to include only what's used
###

# MashaAllah