# -*- coding: utf-8 -*-


def latest_articles(db, query="article.id greater than 0", orderfield='created_on', order='desc', limit=(0, 10)):
    orderby = ~db.article[orderfield] if order == 'desc' else db.article[orderfield]
    return db.smart_query([db.article[field] for field in db.article.fields], query).select(orderby=orderby, limitby=limit)

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
