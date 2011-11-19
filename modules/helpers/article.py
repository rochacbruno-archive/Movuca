# -*- coding: utf-8 -*-


def latest_articles(db, query=None, order=None, limit=None):
    return db(db.article.id > 0).select()
