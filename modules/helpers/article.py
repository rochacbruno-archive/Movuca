# -*- coding: utf-8 -*-


def latest_articles(db, query="article.id greater than 0", orderfield='created_on', order='desc', limit=(0, 10)):
    orderby = ~db.article[orderfield] if order == 'desc' else db.article[orderfield]
    return db.smart_query([db.article[field] for field in db.article.fields], query).select(orderby=orderby, limitby=limit)


def related_articles(db, tags, exclude):
    query = (db.article.tags.contains(tags)) & (db.article.id != exclude)
    rows = db(query).select(orderby="<random>", limitby=(0, 5))
    return rows


therms = [('&', 'and'),
        ('|', 'or'),
        ('~', 'not'),
        ('==', '=='),
        ('<', '<'),
        ('>', '>'),
        ('<=', '<='),
        ('>=', '>='),
        ('<>', '!='),
        ('=<', '<='),
        ('=>', '>='),
        ('=', '=='),
        (' less or equal than ', '<='),
        (' greater or equal than ', '>='),
        (' equal or less than ', '<='),
        (' equal or greater than ', '>='),
        (' less or equal ', '<='),
        (' greater or equal ', '>='),
        (' equal or less ', '<='),
        (' equal or greater ', '>='),
        (' not equal to ', '!='),
        (' not equal ', '!='),
        (' equal to ', '=='),
        (' equal ', '=='),
        (' equals ', '!='),
        (' less than ', '<'),
        (' greater than ', '>'),
        (' starts with ', 'startswith'),
        (' ends with ', 'endswith'),
        (' is ', '==')]
