#!/usr/bin/python
# -*- coding: utf-8 -*-

from movuca import Access, DataBase
from datamodel.article import Article, ContentType
db = DataBase()
auth = Access(db)
content_type = ContentType(db)
article = Article(db)


@auth.requires_login()
def index():
    return dict(message="teste")


def articles():
    return SQLFORM(article.entity, formstyle='divs').process()


def user():
    return dict(form=auth())


def download():
    return response.download(request, db)
