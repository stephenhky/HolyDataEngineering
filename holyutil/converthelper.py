
import warnings

from reformedcatutils.biblebooks import books2idx, idx2books


class BaseSQLiteToJSONConverter:
    def __init__(self, dbconn):
        self.dbconn = dbconn
        self.cursor = self.dbconn.cursor()

    def convert(self, book, chapter, verse, preprocess=lambda x: x):
        bookidx = books2idx[book]
        query = 'select Scripture from Bible where book={} and chapter={} and verse={}'.format(bookidx, chapter, verse)
        iterator = self.cursor.execute(query)
        texts = [text for text in iterator]
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


