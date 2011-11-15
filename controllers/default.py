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
    # this workaround is awful, but it works on GAE. I need a better solution.
    if request.env.web2py_runtime_gae:
        objs = {
            "auth_user": "from movuca import DataBase, Access;db = DataBase();Access(db)"
        }
        tablename = request.args(0).split(".")[0]
        if tablename in objs:
            exec(objs[tablename])
        return response.download(request, db)
    else:
        import os
        response.stream(os.path.join(request.folder, 'uploads', request.args(0)))
