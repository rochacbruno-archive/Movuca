#!/usr/bin/python
# -*- coding: utf-8 -*-

from custom import Access, DataBase
#from datamodel.user import User, Category
db = DataBase()
auth = Access(db)
#auth_user = User(auth=auth)
#cat = Category(db)


@auth.requires_login()
def index():
    return dict(message="teste")


def user():
    return dict(form=auth())


def download():
    return response.download(request, db)
