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
### Lib Imports ###
import argparse
import sys
from os import system
import random
import copy
### My Imports ###
from shared import *
### Globals ###
cards = []
args_dict = dict()
# key: python name -- value: db col name
trans_dict = {'eng': 'english',
              'kana': 'kana',
              'kanji': 'kanji',
              'pres_aff': 'kana_pres_aff',
              'pres_neg': 'kana_pres_neg',
              'past_aff': 'kana_past_aff',
              'past_neg': 'kana_past_neg',
              'type':   'word_type'}
### Functions ###
def parse_args():
    global args_dict
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lesson', nargs='+', type=int, metavar='<lesson num>',
                        help='Which genki lesson to study')
    # options: all, std, i_adj, na_adj, adj, ru_verb, u_verb, irr_verb, verb
    parser.add_argument('-t', '--type', nargs='+', metavar='<word type>',
                        help='Filters words based on word type')
    # options: eng, kana, kanji,
    # future options: kana-pres-aff, kana-pres-neg, kana-past-aff, kana-past-neg, kana-short-pres-aff, kana-short-pres-neg, kana-short-past-aff, kana-short-past-neg, kana-te-form
    # future options: kanj-pres-aff, kanj-pres-neg, kanj-past-aff, kanj-past-neg, kanj-short-pres-aff, kanj-short-pres-neg, kanj-short-past-aff, kanj-short-past-neg, kanj-te-form
    parser.add_argument('-s1', '--side1', nargs='+', default=['kana'], metavar='<col name>',
                        help='Columns to show on first side of card')
    parser.add_argument('-s2', '--side2', nargs='+', default=['eng'], metavar='<col name>',
                        help='Columns to show on second side of card')
    parser.add_argument('-s3', '--side3', nargs='+', metavar='<col name>',
                        help='Columns to show on third side of card')
    # preset options: kana-eng, eng-kana, kana-kanj, kanj-kana, kanj-eng, eng-kanj, 
    parser.add_argument('-p', '--preset', nargs=1, metavar='<preset num>',
                        help='Specify preset column arrangement')
    parser.add_argument('-r', '--reverse', action=argparse.BooleanOptionalAction, default=False,
                        help='reverse the order in which the card sides are shown')
    parser.add_argument('-d', '--double', action=argparse.BooleanOptionalAction, default=False,
                        help='The specified card and its reverse will be added to the study deck')
    parser.add_argument('--comp-kana-verbs', action=argparse.BooleanOptionalAction, default=True,
                        help='When true, sides of cards with kana verbs will appear with its affirmative and negative conjugations')
    parser.add_argument('--comp-kanj-verbs', action=argparse.BooleanOptionalAction, default=False,
                        help='When true, sides of cards with kanji verbs will appear with its affirmative and negative conjugations')
    # options: pres, past, short, short-past, te-form
    parser.add_argument('--comp-verbs-tense', nargs=1, default='pres', metavar='<verb tense>',
                        help='Change this to change which conjugation verbs are shown with when --comp-kan?-verbs option is set')
    parser.add_argument('--comp-kana-adjs', action=argparse.BooleanOptionalAction, default=True,
                        help='When true, sides of cards with kana adjectives will appear with its affirmative and negative conjugations')
    parser.add_argument('--comp-kanj-adjs', action=argparse.BooleanOptionalAction, default=False,
                        help='When true, sides of cards with kanji adjectives will appear with its affirmative and negative conjugations')
    parser.add_argument('--comp-adjs-tense', nargs=1, default='pres', metavar='<adj tense>',
                        help='Change this to change which conjugation adjectives are shown with when --comp-kan?-adjs option is set')
    parser.add_argument('-w', '--working-set', nargs=1, type=int, metavar='<working set size>',
                        help='Controls the size of the largest round robin pool')
    args_dict = vars(parser.parse_args())

def print_err(msg: str):
    print("Error: " + msg)
    print("Exiting")
    exit(1)

def gen_cards():
    global cards
    select_statement = gen_select_sql()
    cols = get_cols_list()

    with get_db_connection() as db_conn:
        db_cursor = db_conn.cursor()
        db_cursor.execute(select_statement)
        selected_rows = db_cursor.fetchall()
    add_db_rows_to_cards(selected_rows, cols)

def gen_select_sql() -> str:
    # SELECT kana || coalesce(kana_pres_aff || ';', "") || coalesce(kana_pres_neg || ';', "") AS verb FROM words;
    select_statement = 'SELECT '
    cols_list = get_translated_cols_list()
    for col in cols_list:
        select_statement += col + ', '
    select_statement = select_statement[0:-2]
    select_statement += ' FROM words'

    if(args_dict['lesson'] is not None):
        select_statement += ' WHERE lesson IN ('
        for e in args_dict['lesson']:
            select_statement += str(e) + ', '
        select_statement = select_statement[0:-2] + ')'
        if(args_dict['type'] is not None):
            select_statement += ' AND word_type IN ('
            for e in args_dict['type']:
                select_statement += '\'' + str(e) + '\', '
            select_statement = select_statement[0:-2] + ')'
        return select_statement
    if(args_dict['type'] is not None):
        select_statement += ' WHERE word_type IN ('
        for e in args_dict['type']:
            select_statement += '\'' + str(e) + '\', '
        select_statement = select_statement[0:-2] + ')'
    return select_statement

def get_cols_list() -> [str]:
    col_list = ['type']
    for col in args_dict['side1']:
        if(col not in col_list):
            col_list.append(col)
    for col in args_dict['side2']:
        if(col not in col_list):
            col_list.append(col)
    if(args_dict['side3']  is not None):
        for col in args_dict['side3']:
            if(col not in col_list):
                col_list.append(col)
    if(args_dict['comp_kana_verbs']):
        if((args_dict['comp_verbs_tense'] + '_pres') not in col_list):
            col_list.append(args_dict['comp_verbs_tense'] + '_aff')
        if((args_dict['comp_verbs_tense'] + '_neg') not in col_list):
            col_list.append(args_dict['comp_verbs_tense'] + '_neg')
    return col_list

def get_translated_cols_list() -> [str]:
    cols_list = get_cols_list()
    for i in range(0, len(cols_list)):
        if(cols_list[i] not in trans_dict):
                print_err('Specified side/column parameter: \'' + cols_list[i] + '\' not valid')
        cols_list[i] = trans_dict[cols_list[i]]
    return cols_list

def add_db_rows_to_cards(rows, col_names):
    global cards
    for row in rows:
        cur_card = []
        side1_text = ''
        for col in args_dict['side1']:
            tmp_text = row[col_names.index(col)] 
            # TODO
            # if(args_dict['comp_kana_verbs'] and col == 'kana_v'):
            side1_text += tmp_text + '\n'
        cur_card.append(side1_text[0:-1])
        side2_text = ''
        for col in args_dict['side2']:
            side2_text += row[col_names.index(col)] + '\n'
        cur_card.append(side2_text[0:-1])
        if(args_dict['side3'] is not None):
            side3_text = ''
            for col in args_dict['side3']:
                if(row[col_names.index(col)] is not None):
                    side3_text += row[col_names.index(col)] + '\n'
            if(side3_text != ''):
                cur_card.append(side3_text[0:-1])
        if(args_dict['reverse']):
            cur_card.reverse()
        if(args_dict['double']):
            double_card = copy.deepcopy(cur_card)
            double_card.reverse()
            cards.append(double_card)
        cards.append(cur_card)

def study():
    global cards
    print_cards()
    input('')
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
            repeat_flag = False
            # dbprint(cur_cards[cur_idx])
            for side in cur_cards[cur_idx]:
                print(side)
                resp = input('')
                if(len(resp) > 0):
                    if(resp[0] == 'q'):
                        system('clear')
                        return (review_count, repeat_count)
                    repeat_flag = True
            if(repeat_flag):
                    repeat_list.append(cur_cards.pop(cur_idx))
                    repeat_count += 1
            else:
                cur_cards.pop(cur_idx)
            review_count += 1
    except Exception as e:
        pass
    finally:
        system('clear')
        return (review_count, repeat_count)

def print_cards():
    for card in cards:
        print('|', end='')
        for side in card:
            print(side + '|', end='')
        print()

def run():
    parse_args()
    gen_cards()
    review_count, repeat_count = study()
    print(f'{review_count} reviews')
    print(f'{repeat_count} repeats')

if(__name__ == '__main__'):
    run()
