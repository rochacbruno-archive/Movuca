# -*- coding: utf-8 -*-


def latest_articles(db, query="article.id greater than 0", orderfield='created_on', order='desc', limit=(0, 10)):
    orderby = ~db.article[orderfield] if order == 'desc' else db.article[orderfield]
    return db.smart_query([db.article[field] for field in db.article.fields], query).select(orderby=orderby, limitby=limit)


def related_articles(db, tags, category, exclude):
    if not tags:
        tags = ['default']
    from gluon import current
    if not current.request.env.web2py_runtime_gae:
        query = (db.article.tags.contains(tags)) & (db.article.id != exclude) & (db.article.draft == False)
        rows = related(db, query)
    else:
        query = (db.article.category_id == category) & (db.article.id != exclude) & (db.article.draft == False)
        rows = related_gae(db, query)
    return rows


def related_gae(db, query):
    import random
    return db(query).select().sort(lambda row: random.random())[:4]


def related(db, query):
    return db(query).select(orderby="<random>", limitby=(0, 5))

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
