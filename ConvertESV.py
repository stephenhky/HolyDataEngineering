
import sqlite3
from argparse import ArgumentParser
import os
import json

from reformedcatutils.biblebooks import books2idx, numchaps

from holyutil.converthelper import BaseSQLiteToJSONConverter


def get_argparser():
    argparser = ArgumentParser(description='Convert ESV Bible to list of JSONs')
    argparser.add_argument('inputsqlitepath', help='path of the SQLite file of ESV Bible')
    argparser.add_argument('jsonpath', help='path of the output JSON')
    return argparser


if __name__ == '__main__':
    args = get_argparser().parse_args()
    dbpath = args.inputsqlitepath
    if not os.path.exists(dbpath):
        raise FileNotFoundError('File not found: {}'.format(dbpath))
    jsonpath = args.jsonpath
    jsondir = os.path.dirname(jsonpath)
    if not os.path.isdir(jsondir):
        raise FileNotFoundError('Not a valid directory: {}'.format(jsondir))

    dbconn = sqlite3.connect(dbpath)
    converter = BaseSQLiteToJSONConverter(dbconn)
    outputfile = open(jsonpath, 'w')
    for book in books2idx.keys():
        for chapter in range(1, numchaps[book]+1):
            maxverse = converter.find_number_of_verses(book, chapter)
            for verse in range(1, maxverse+1):
                bibversedict = converter.convert(book, chapter, verse)
                outputfile.write(json.dumps(bibversedict)+'\n')
    outputfile.close()
