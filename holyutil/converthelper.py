
import warnings
import re

from reformedcatutils.biblebooks import books2idx, idx2books


class BaseSQLiteToJSONConverter:
    def __init__(self, dbconn):
        self.dbconn = dbconn
        self.cursor = self.dbconn.cursor()

    def find_number_of_verses(self, book, chapter):
        query = 'select max(verse) from Bible where book={} and chapter={}'.format(books2idx[book], chapter)
        maxverse = max([item[0] for item in self.cursor.execute(query)])
        return maxverse

    def convert(self, book, chapter, verse, preprocess=lambda x: x):
        bookidx = books2idx[book]
        query = 'select Scripture from Bible where book={} and chapter={} and verse={}'.format(bookidx, chapter, verse)
        iterator = self.cursor.execute(query)
        texts = [text[0] for text in iterator]
        if len(texts) == 0:
            return {}
        elif len(texts) == 1:
            return {
                'book': book,
                'chapter': chapter,
                'verse': verse,
                'text': preprocess(texts[0])
            }
        else:
            warnings.warn('More than one return for {} {}:{}'.format(book, chapter, verse))
            return {
                'book': book,
                'chapter': chapter,
                'verse': verse,
                'text': preprocess(texts[0])
            }


def esv_preprocess_text(s):
    to_removes = [r'\<[Ff][RrIi]>', r'\<Blue>.+\</Blue>']
    for to_remove in to_removes:
        s = re.sub(to_remove, '', s)
    s = re.sub(r'\s+', ' ', s)
    return s