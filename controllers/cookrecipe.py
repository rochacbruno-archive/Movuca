#!/usr/bin/python
# -*- coding: utf-8 -*-

# from gluon.tools import Auth
# auth = Auth(DAL(None))

from handlers.cookrecipe import CookRecipe


def addtobookbutton():
    cookrecipe = CookRecipe()
    return cookrecipe.add_to_book_button()


def removefrombook():
    cookrecipe = CookRecipe('remove_from_book')
    return cookrecipe.add_to_book_button()


def addtobook():
    cookrecipe = CookRecipe('add_to_book')
    return cookrecipe.add_to_book_button()
