#!/usr/bin/python
# -*- coding: utf-8 -*-

# from gluon.tools import Auth
# auth = Auth(DAL(None))

from movuca import DataBase, User
from datamodel.article import Category, ContentType, Article
from datamodel.contenttypes import CookRecipeBook

db = DataBase([User, ContentType, Category, Article, CookRecipeBook])


def addtobook():
    return db.CookRecipeBook.fields
