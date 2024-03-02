# TODO
# Study scheduling:
#   add in working_set_size functionality where the size of the round robin pool is given an upper limit
# UI
#   add in tracker on top bar for the percentage of the way through the working set you are
#   add in counter for number of cards added to the review_list

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
db_cols_trans_dict = {'type': 'word_type',
                      'lesson': 'lesson',
                      'kana': 'kana',
                      'eng': 'english',
                      'kanji': 'kanji',
                      'kn-pr-af': 'kana_pres_aff',
                      'kn-pr-ng': 'kana_pres_neg',
                      'kn-pt-af': 'kana_past_aff',
                      'kn-pt-ng': 'kana_past_neg',
                      'kn-te': 'kana_te_form',
                      'kj-pr-af': 'kanji_pres_aff',
                      'kj-pr-ng': 'kanji_pres_neg',
                      'kj-pt-af': 'kanji_past_aff',
                      'kj-pt-ng': 'kanji_past_neg',
                      'kj-te': 'kanji_te_form',
                      }
db_type_trans_dict = {'std': "'std'",
                       'i-adj': "'i_adj'",
                       'na-adj': "'na_adj'",
                       'adj': "'i_adj', 'na_adj'",
                       'u-verb': "'u_verb'",
                       'ru-verb': "'ru_verb'",
                       'irr-verb': "'irr_verb'",
                       'verb': "'u_verb', 'ru_verb', 'irr_verb'"
                       }
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
    parser.add_argument('-k', '--kanji', action=argparse.BooleanOptionalAction, default=False,
                        help='Only study cards with kanji')
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
    #   add text to card
    #       logic for --reverse and --double
    # side2
    # side3
    # don't add card if less than two sides are populated
    global cards
    for i in range(0, get_num_of_cards()):
        cards.append([None, None, None])

    with get_db_connection() as db_conn:
        db_cursor = db_conn.cursor()
        for col in args_dict['side1']:
            db_cursor.execute(gen_sql(col))
            res = db_cursor.fetchall()
            for i in range(0, len(cards)):
                if(res[i][0] is None):
                    continue
                if(cards[i][0] is None):
                    cards[i][0] = res[i][0]
                else:
                    cards[i][0] += '\n' + res[i][0]
        for col in args_dict['side2']:
            db_cursor.execute(gen_sql(col))
            res = db_cursor.fetchall()
            for i in range(0, len(cards)):
                if(res[i][0] is None):
                    continue
                if(cards[i][1] is None):
                    cards[i][1] = res[i][0]
                else:
                    cards[i][1] += '\n' + res[i][0]
        if(args_dict['side3'] is not None):
            for col in args_dict['side3']:
                db_cursor.execute(gen_sql(col))
                res = db_cursor.fetchall()
                for i in range(0, len(cards)):
                    if(res[i][0] is None):
                        continue
                    if(cards[i][2] is None):
                        cards[i][2] = res[i][0]
                    else:
                        cards[i][2] += '\n' + res[i][0]
    if(args_dict['reverse']):
        for card in cards:
            card.reverse()
    if(args_dict['double']):
        double_cards = []
        for card in cards:
            new_card = copy.deepcopy(card)
            new_card.reverse()
            double_cards.append(new_card)
        cards = cards + double_cards
    cards = [card for card in [[side for side in card if side is not None] for card in cards] if card]

def gen_where_clause() -> str:
    sql_where_clauses = []
    if(args_dict['lesson'] is not None):
        cur_clause = db_cols_trans_dict['lesson'] + ' IN ('
        for les in args_dict['lesson']:
            cur_clause += str(les) + ', '
        cur_clause = cur_clause[0:-2] + ')'
        sql_where_clauses.append(cur_clause)
    if(args_dict['type'] is not None):
        cur_clause = db_cols_trans_dict['type'] + ' IN ('
        for typ in args_dict['type']:
            cur_clause += db_type_trans_dict[typ] + ', '
        cur_clause = cur_clause[0:-2] + ')'
        sql_where_clauses.append(cur_clause)
    if(args_dict['kanji']):
        cur_clause = 'kanji IS NOT NULL'
        sql_where_clauses.append(cur_clause)
    if(not sql_where_clauses):
        return ''
    sql_where = 'WHERE '
    for clause in sql_where_clauses[0:-1]:
        sql_where += clause + ' AND '
    sql_where += sql_where_clauses[-1]
    return sql_where

def gen_select_clause(cur_col: str) -> str:
    # SELECT kana || coalesce(kana_pres_aff || ';', "") || coalesce(kana_pres_neg || ';', "") AS verb FROM words;
    if(args_dict['comp_kana_verbs'] and cur_col == 'kana'):
        # TODO comp_verbs_tense is apparently an arr so make this general
        match args_dict['comp_verbs_tense'][0]:
            case 'pres':
                tense1 = db_cols_trans_dict['kn-pr-af']
                tense2 = db_cols_trans_dict['kn-pr-ng']
            case 'past':
                tense1 = db_cols_trans_dict['kn-pt-af']
                tense2 = db_cols_trans_dict['kn-pt-ng']
            case 'te-form':
                tense1 = db_cols_trans_dict['kn-te']
                tense2 = None
            case _:
                tense1 = db_cols_trans_dict['kn-pr-af']
                tense2 = db_cols_trans_dict['kn-pr-ng']
        select_statement = "SELECT kana || coalesce(';' || " + tense1 + ", '')"
        if(tense2 is not None):
            select_statement += " || coalesce(';' || "  + tense2 + ",'')"
        select_statement += " FROM words"
        return select_statement
    return 'SELECT ' + db_cols_trans_dict[cur_col] + ' FROM words'

def gen_sql(col) -> str:
    return gen_select_clause(col) + ' ' + gen_where_clause() + ' ORDER BY ROWID'

def get_num_of_cards() -> int:
    with get_db_connection() as db_conn:
        db_cursor = db_conn.cursor()
        db_cursor.execute('SELECT count(*) FROM words ' + gen_where_clause())
        res = db_cursor.fetchall()
        return res[0][0]

def study():
    global cards
    system('clear')
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
    if(not cards):
        print('NO CARDS IN STUDY DECK!')
        return
    spacing = 45
    for card in cards[0:-1]:
        for side in card:
            text_len = len(side)
            print(side, end='')
            print(' ' * (spacing - text_len), end='')
        print()
    for side in cards[-1]:
        text_len = len(side)
        print(side, end='')
        print(' ' * (spacing - text_len), end='')
    print()

def run():
    parse_args()
    gen_cards()
    review_count, repeat_count = study()
    print(f'{review_count} reviews')
    print(f'{repeat_count} repeats')

if(__name__ == '__main__'):
    run()
