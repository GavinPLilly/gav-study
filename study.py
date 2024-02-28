# Read csv and create test array
# Run study algo
# TODO
# Study scheduling:
#   add in working_set_size functionality where the size of the round robin pool is given an upper limit
# UI
#   add in tracker on top bar for the percentage of the way through the working set you are
#   add in counter for number of cards added to the review_list
# Database
#   add database instead of csv
#   > Table for words
#   > rows:
#       > Primary key: id
#       > Card type: {normal, verb, adjective} // maybe tense as well?
#       > kana: text
#       > English: text
#       > Kanji: text
#       > kana_pres_aff: text
#       > kana_pres_neg: text
#       > kana_past_aff: text
#       > kana_past_neg: text
#       > kanji_pres_aff: text
#       > kanji_pres_neg: text
#       > kanji_past_aff: text
#       > kanji_past_neg: text
################################################
### Imports ###
import sys
from os import system
import random
import copy
### Globals ###
cards = []
KANA_ENG = (0, 1)
KANA_KANJI = (0, 2)
ENG_KANJI = (1, 2)
DEFAULT_CARD_TYPES = [KANA_ENG]
DEFAULT_ARGS = {'card_types': DEFAULT_CARD_TYPES, 'double_sided': False, 'reversed': True, 'working_set_size': 0}
ARGS = DEFAULT_ARGS
### Functions ###
def get_filename() -> str:
    return sys.argv[1:]

def print_err(msg: str):
    print("Error: " + msg)
    print("Exiting")
    exit(1)

"""
-t=
--type=0
-d
--double
"""
def process_args():
    pass
    # global DEFAULT_ARGS
    # for arg in sys.argv:
    #     if(arg.startswith('-')):
    #         arg = arg[1:]
    #         if(len(arg) == 0):
    #             print_err('Argument name must follow dash \'-\'')
    #         if(arg.startswith('t')):
    #             arg = arg[1:]
    #             if(len(arg) == 0):
    #                 print_err('-t argument takes a value. \'=\' must follow -t')
    #             if(arg.startswith('=') == False):
    #                 print_err('-t argument takes a value. \'=\' must follow -t')
    #             arg[1:]
    #             ARGS['card_types'] 

def add_card(line: str):
    global cards
    global ARGS
    line = line.strip()
    values = line.split(',')
    for card_type in ARGS['card_types']:
        if(card_type[0] >= len(values) or card_type[1] >= len(values)):
            continue
        if(values[card_type[0]] == '' or values[card_type[1]] == ''):
            continue
        if(ARGS['reversed'] == True):
            front = values[card_type[1]]
            back = values[card_type[0]]
        else:
            front = values[card_type[0]]
            back = values[card_type[1]]
        if(ARGS['double_sided'] == True):
            cards.append((back, front))
        cards.append((front, back))

def add_cards_from_csv(filenames: [str]):
    global cards
    for filename in filenames:
        with open(filename, encoding='utf-8') as csv_file:
            lines = list(csv_file)
            for line in lines:
                add_card(line)

def study():
    global cards
    cur_cards = copy.deepcopy(cards)
    repeat_list = []
    review_count = 0
    repeat_count = 0
    try:
        while True:
            system('clear')
            if(len(cur_cards) == 0):
                if(len(repeat_list) > 0):
                    cur_cards = repeat_list
                    repeat_list = []
                    print('~~~~~~~~~~~~~~~~~~~~~~')
                    print('reviewing missed items')
                    print('~~~~~~~~~~~~~~~~~~~~~~')
                else:
                    cur_cards = copy.deepcopy(cards)
                    print('~~~~~~~~~~~~~~~~')
                    print('refreshing cards')
                    print('~~~~~~~~~~~~~~~~')
            cur_idx = random.randint(0, len(cur_cards) - 1);
            print(cur_cards[cur_idx][0])
            resp = input('')
            if(len(resp) > 0 and resp[0] == 'q'):
                break
            print(cur_cards[cur_idx][1])
            resp += input('')
            if(len(resp) > 0):
                if(resp[0] == 'q'):
                    break
                repeat_list.append(cur_cards.pop(cur_idx))
                repeat_count += 1
            else:
                cur_cards.pop(cur_idx)
            review_count += 1
    except Exception as e:
        pass
    finally:
        system('clear')
        print(f'{review_count} reviews')
        print(f'{repeat_count} repeats')

def run():
    add_cards_from_csv(get_filename())
    study()
run()
################################################
"""
import random
import copy

kata_romanji_arr = [('ア', 'a'), ('イ', 'i'), ('ウ', 'u'), ('エ', 'e'), ('オ', 'o'), ('カ', 'ka'), ('キ', 'ki'), ('ク', 'ku'), ('ケ', 'ke'), ('コ', 'ko'), ('サ', 'sa'), ('シ', 'shi'), ('ス', 'su'), ('セ', 'se'), ('ソ', 'so'), ('タ', 'ta'), ('チ', 'chi'), ('ツ', 'tsu'), ('テ', 'te'), ('ト', 'to'), ('ナ', 'na'), ('ニ', 'ni'), ('ヌ', 'nu'), ('ネ', 'ne'), ('ノ', 'no'), ('ハ', 'ha'), ('ヒ', 'hi'), ('フ', 'fu'), ('ヘ', 'he'), ('ホ', 'ho'), ('マ', 'ma'), ('ミ', 'mi'), ('ム', 'mu'), ('メ', 'me'), ('モ', 'mo'), ('ヤ', 'ya'), ('ユ', 'yu'), ('ヨ', 'yo'), ('ラ', 'ra'), ('リ', 'ri'), ('ル', 'ru'), ('レ', 're'), ('ロ', 'ro'), ('ワ', 'wa'), ('ヲ', 'wo'), ('ン', 'n')]
# kata_romanji_arr = [('ア', 'a'), ('イ', 'i'), ('ウ', 'u'), ('エ', 'e'), ('オ', 'o')]
cur_kata_romanji_arr = copy.deepcopy(kata_romanji_arr)
wrong_list = []

while True:
    if(len(cur_kata_romanji_arr) == 0):
        if(len(wrong_list) > 0):
            cur_kata_romanji_arr = wrong_list
            wrong_list = []
            print('reviewing missed kana')
        else:
            cur_kata_romanji_arr = copy.deepcopy(kata_romanji_arr)
            print('refreshing arr')
    cur_idx = random.randint(0, len(cur_kata_romanji_arr) - 1);
    print(cur_kata_romanji_arr[cur_idx][1])
    resp = input('')
    print(cur_kata_romanji_arr[cur_idx][0])
    resp += input('')
    if(len(resp) > 0):
        wrong_list.append(cur_kata_romanji_arr.pop(cur_idx))
    else:
        cur_kata_romanji_arr.pop(cur_idx)

# kata_arr = ["ア", "イ", "ウ", "エ", "オ", "カ", "キ", "ク", "ケ", "コ", "サ", "シ", "ス", "セ", "ソ", "タ", "チ", "ツ", "テ", "ト", "ナ", "ニ", "ヌ", "ネ", "ノ", "ハ", "ヒ", "フ", "ヘ", "ホ", "マ", "ミ", "ム", "メ", "モ", "ヤ", "ユ", "ヨ", "ラ", "リ", "ル", "レ", "ロ", "ワ", "ヲ", "ン", ]
# romanji_arr = ['a', 'i', 'u', 'e', 'o', 'ka', 'ki', 'ku', 'ke', 'ko', 'sa', 'shi', 'su', 'se', 'so', 'ta', 'chi', 'tsu', 'te', 'to', 'na', 'ni', 'nu', 'ne', 'no', 'ha', 'hi', 'fu', 'he', 'ho', 'ma', 'mi', 'mu', 'me', 'mo', 'ya', 'yu', 'yo', 'ra', 'ri', 'ru', 're', 'ro', 'wa', 'wo', 'n']
"""
