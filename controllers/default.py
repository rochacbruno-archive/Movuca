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


#@auth.requires_login()
def index():
    from handlers.home import Home
    home = Home()
    return home.render()


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
    flnm = request.args(0)
    if request.env.web2py_runtime_gae:
        tbl, fld = flnm.split('.')[:2]
        from config import Config
        config = Config()
        config._db.define_table(tbl, Field(fld, "upload"), migrate=False)
        return response.download(request, config._db)
    else:
        import os
        response.stream(os.path.join(request.folder, 'uploads', flnm))
