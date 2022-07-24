
import sqlite3
from argparse import ArgumentParser
import os

from dotenv import load_dotenv
from reformedcatutils.biblebooks import books2idx, numchaps
import boto3
from tqdm import tqdm

from holyutil.converthelper import BaseSQLiteToJSONConverter


def get_argparser():
    argparser = ArgumentParser(description='Convert NIV Bible to list of JSONs')
    argparser.add_argument('inputsqlitepath', help='path of the SQLite file of ESV Bible')
    argparser.add_argument('dynamodb_table', help='name of the DynamoDB table')
    argparser.add_argument('--aws_access_key_id', type=str, default=None, help='AWS Access Key ID')
    argparser.add_argument('--aws_secret_access_key', type=str, default=None, help='AWS Secret Access Key')
    return argparser


if __name__ == '__main__':
    args = get_argparser().parse_args()
    dbpath = args.inputsqlitepath
    if not os.path.exists(dbpath):
        raise FileNotFoundError('File not found: {}'.format(dbpath))
    if args.aws_access_key_id is None or args.aws_secret_access_key is None:
        load_dotenv()
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    else:
        aws_access_key_id = args.aws_access_key_id
        aws_secret_access_key = args.aws_secret_access_key

    client = boto3.client('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    table = dynamodb.Table(args.dynamodb_table)

    dbconn = sqlite3.connect(dbpath)
    converter = BaseSQLiteToJSONConverter(dbconn)
    for book in tqdm(books2idx.keys()):
        for chapter in range(1, numchaps[book]+1):
            maxverse = converter.find_number_of_verses(book, chapter)
            for verse in range(1, maxverse+1):
                bibversedict = converter.convert(book, chapter, verse, preprocess=lambda s: s)
                bibversedict['bibid'] = '{}-{}-{}'.format(book, chapter, verse)

                table.put_item(Item=bibversedict)
