
import os
import sqlite3
import json
from argparse import ArgumentParser
from collections import defaultdict

from reformedcatutils.biblebooks import books2idx, idx2books, numchaps

from holyutil.converthelper import BaseSQLiteToJSONConverter


def get_argparser():
    argparser = ArgumentParser(description='To get the maximum number of verses for each chapter and store it in a JSON.')
    argparser.add_argument('bible_sqlite_path', help='path of the Bible in sqlite')
    argparser.add_argument('output_json', help='path of output JSON')
    return argparser


if __name__ == '__main__':
    args = get_argparser().parse_args()
    dbpath = args.bible_sqlite_path
    if not os.path.exists(dbpath):
        raise FileNotFoundError('File not found: {}'.format(dbpath))
    output_json = args.output_json
    jsondir = os.path.dirname(output_json)
    if not os.path.isdir(jsondir):
        raise FileNotFoundError('Not a valid directory: {}'.format(jsondir))

    dbconn = sqlite3.connect(dbpath)
    converter = BaseSQLiteToJSONConverter(dbconn)
    versedict = defaultdict(lambda : {})
    for book in books2idx.keys():
        for chapter in range(1, numchaps[book]+1):
            maxverse = converter.find_number_of_verses(book, chapter)
            versedict[book][chapter] = maxverse
    versedict = dict(versedict)

    json.dump(versedict, open(args.output_json, 'w'))
