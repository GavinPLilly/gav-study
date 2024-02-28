import csv
import sys
import sqlite3
from sqlite3 import Error

def get_filenames() -> [str]:
    return sys.argv[1:]

def print_err(msg: str):
    print("Error: " + msg)
    print("Exiting")
    exit(1)

def get_db_connection():
    try:
        return sqlite3.connect('/home/gavin/study/db/study.sqlite')
    except Exception as e:
        print(e)
        print_err('Error connecting to database')

def add_files_to_db(filenames: [str]):
    for filename in filenames:
        add_file_to_db(filename)

def add_file_to_db(filename: str):
    with open(filename, encoding='utf-8', newline='') as csv_file:
        csv_dict_reader = csv.DictReader(csv_file)
        processed_line_dict_arr = process_csv_dict_reader_values(csv_dict_reader)
    with get_db_connection() as db_conn:
        db_cursor = db_conn.cursor()
        db_cursor.execute('begin')
        for line in processed_line_dict_arr:
            insert_statement = gen_insert_sql(line)
            db_cursor.execute(insert_statement, tuple(line.values()))
        db_cursor.execute('commit')

def process_csv_dict_reader_values(csv_dict_reader: object):
    processed_line_dict_arr = []
    for line_dict in csv_dict_reader:
        processed_line_dict = dict()
        if(line_dict['word_type'] == ''):
            print_err('word_type field must contain value')
        processed_line_dict['word_type'] = line_dict['word_type']
        processed_line_dict['lesson'] = int(line_dict['lesson'])
        if(line_dict['kana'] == ''):
            print_err('kana field must contain value')
        processed_line_dict['kana'] = line_dict['kana']
        if(line_dict['english'] == ''):
            print_err('english field must contain value')
        processed_line_dict['english'] = line_dict['english']
        if(line_dict['kanji'] != ''):
            processed_line_dict['kanji'] = line_dict['kanji']
        if(line_dict['kana_pres_aff'] != ''):
            processed_line_dict['kana_pres_aff'] = line_dict['kana_pres_aff']
        if(line_dict['kana_pres_neg'] != ''):
            processed_line_dict['kana_pres_neg'] = line_dict['kana_pres_neg']
        if(line_dict['kana_past_aff'] != ''):
            processed_line_dict['kana_past_aff'] = line_dict['kana_past_aff']
        if(line_dict['kana_past_neg'] != ''):
            processed_line_dict['kana_past_neg'] = line_dict['kana_past_neg']
        if(line_dict['kana_short_pres_aff'] != ''):
            processed_line_dict['kana_short_pres_aff'] = line_dict['kana_short_pres_aff']
        if(line_dict['kana_short_pres_neg'] != ''):
            processed_line_dict['kana_short_pres_neg'] = line_dict['kana_short_pres_neg']
        if(line_dict['kana_short_past_aff'] != ''):
            processed_line_dict['kana_short_past_aff'] = line_dict['kana_short_past_aff']
        if(line_dict['kana_short_past_neg'] != ''):
            processed_line_dict['kana_short_past_neg'] = line_dict['kana_short_past_neg']
        if(line_dict['kana_te_form'] != ''):
            processed_line_dict['kana_te_form'] = line_dict['kana_te_form']
        if(line_dict['kanji_pres_aff'] != ''):
            processed_line_dict['kanji_pres_aff'] = line_dict['kanji_pres_aff']
        if(line_dict['kanji_pres_neg'] != ''):
            processed_line_dict['kanji_pres_neg'] = line_dict['kanji_pres_neg']
        if(line_dict['kanji_past_aff'] != ''):
            processed_line_dict['kanji_past_aff'] = line_dict['kanji_past_aff']
        if(line_dict['kanji_past_neg'] != ''):
            processed_line_dict['kanji_past_neg'] = line_dict['kanji_past_neg']
        if(line_dict['kanji_short_pres_aff'] != ''):
            processed_line_dict['kanji_short_pres_aff'] = line_dict['kanji_short_pres_aff']
        if(line_dict['kanji_short_pres_neg'] != ''):
            processed_line_dict['kanji_short_pres_neg'] = line_dict['kanji_short_pres_neg']
        if(line_dict['kanji_short_past_aff'] != ''):
            processed_line_dict['kanji_short_past_aff'] = line_dict['kanji_short_past_aff']
        if(line_dict['kanji_short_past_neg'] != ''):
            processed_line_dict['kanji_short_past_neg'] = line_dict['kanji_short_past_neg']
        if(line_dict['kanji_te_form'] != ''):
            processed_line_dict['kanji_te_form'] = line_dict['kanji_te_form']
        if(line_dict['noun_mod_form'] != ''):
            processed_line_dict['noun_mod_form'] = line_dict['noun_mod_form']
        processed_line_dict_arr.append(processed_line_dict)
    return processed_line_dict_arr

def gen_insert_sql(line: dict) -> str:
    insert_statement = 'INSERT INTO words ('
    q_mark_string = ''
    for key in line:
        insert_statement += f'{key}, '
        q_mark_string += '?, '
    if(insert_statement[-2] == ','):
        insert_statement = insert_statement[0:-2]
    if(q_mark_string != '' and q_mark_string[-2] == ','):
        q_mark_string = q_mark_string[0:-2]
    insert_statement += ') VALUES (' + q_mark_string + ')'
    return insert_statement

def run():
    add_files_to_db(get_filenames())

run()
