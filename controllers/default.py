#!/usr/bin/python
# -*- coding: utf-8 -*-

# from movuca import Access, DataBase
# from datamodel.article import Article, ContentType
# db = DataBase()
# auth = Access(db)
# content_type = ContentType(db)
# article = Article(db)
from gluon.tools import Auth
auth = Auth(DAL(None))


@auth.requires_login()
def index():
    return dict(message="teste")


def articles():
    from movuca import Access, DataBase
    from datamodel.article import Article, ContentType
    db = DataBase()
    Access(db)
    ContentType(db)
    article = Article(db)
    return SQLFORM(article.entity, formstyle='divs').process()


def user():
    from movuca import Access, DataBase
    db = DataBase()
    access = Access(db)
    return dict(form=access())


def download():
    return response.download(request, db)
