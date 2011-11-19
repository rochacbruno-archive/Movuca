#!/usr/bin/python
# -*- coding: utf-8 -*-
from handlers.article import Article


def show():
    article = Article('show')
    return article.render()


def edit():
    article = Article('edit')
    return article.render()


def new():
    article = Article('new')
    return article.render()


def delete():
    pass


def list():
    pass


def favorite():
    pass


def comment():
    pass


def vote():
    pass


def book():
    pass
