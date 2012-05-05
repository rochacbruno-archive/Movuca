#!/usr/bin/python
# -*- coding: utf-8 -*-

# from gluon.tools import Auth
# auth = Auth(DAL(None))

from handlers.cookrecipe import CookRecipe


def addtobookbutton():
    cookrecipe = CookRecipe()
    return cookrecipe.add_to_book_button()


def removefrombook():
    cookrecipe = CookRecipe()
    return cookrecipe.remove_from_book()


def addtobook():
    cookrecipe = CookRecipe('add_to_book')
    return cookrecipe.add_to_book_button()

def book():
	cookrecipe = CookRecipe('book')
	return cookrecipe.render('app/cookrecipe/book')
    