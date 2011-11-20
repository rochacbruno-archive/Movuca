#!/usr/bin/python
# -*- coding: utf-8 -*-
from handlers.article import Article


def show():
    article = Article('show')
    article.context.left_sidebar_enabled = True
    return article.render("app/article/show/%s" % article.context.article.content_type_id.viewname)


def edit():
    article = Article('edit')
    return article.render()


def new():
    article = Article('new')
    return article.render()


def delete():
    pass


def list():
    article = Article('list')
    return article.render()


def favorite():
    article = Article('favorite')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def like():
    article = Article('like')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def dislike():
    article = Article('dislike')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def subscribe():
    article = Article('subscribe')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def unfavorite():
    article = Article('unfavorite')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def unlike():
    article = Article('unlike')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def unsubscribe():
    article = Article('unsubscribe')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def undislike():
    article = Article('undislike')
    if not article.context.error:
        return article.action_links()
    else:
        return article.context.error


def comment():
    pass


def vote():
    pass


def book():
    pass


def tag():
    pass
